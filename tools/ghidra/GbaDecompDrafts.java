// Ghidra headless script for Yugioh_DeComp_V2 (milestone Y5).
//
// Two phases, both driven by config/functions.csv (address,name,mode,size,source):
//   funcs   -- disassemble each function in the right mode (TMode context 0=ARM, 1=THUMB) and
//              create a function with the ROM's own name, so callers read `sub_080243A0`, not
//              `FUNC_080243a0`.
//   drafts  -- run the decompiler over every function and write private/ghidra/<name>.c.
//
// Run through scripts/ghidra_drafts.sh; do not call analyzeHeadless by hand.
//
// The output is a DRAFT: Ghidra's C does not compile to the ROM's bytes with agbcc. It exists to
// show the shape of the code (types, loops, branches) to whoever writes the matching C.

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.symbol.SourceType;

public class GbaDecompDrafts extends GhidraScript {

    private static class Row {
        final String name;
        final long addr;
        final long size;
        final boolean thumb;

        Row(String name, long addr, long size, boolean thumb) {
            this.name = name;
            this.addr = addr;
            this.size = size;
            this.thumb = thumb;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            printerr("usage: GbaDecompDrafts.java <funcs|drafts> <functions.csv> <outdir> [--only NAME]");
            return;
        }
        String mode = args[0];
        File csv = new File(args[1]);
        File outDir = new File(args[2]);
        String only = null;
        for (int i = 3; i + 1 < args.length; i++) {
            if (args[i].equals("--only")) {
                only = args[i + 1];
            }
        }

        List<Row> rows = readCsv(csv);
        println("csv: " + rows.size() + " function(s) from " + csv);
        if (only != null) {
            List<Row> one = new ArrayList<>();
            for (Row r : rows) {
                if (r.name.equals(only)) {
                    one.add(r);
                }
            }
            if (one.isEmpty()) {
                printerr("--only " + only + " is not in " + csv);
                return;
            }
            rows = one;
        }

        if (mode.equals("funcs")) {
            createFunctions(rows);
        }
        else if (mode.equals("drafts")) {
            writeDrafts(rows, outDir);
        }
        else {
            printerr("unknown mode '" + mode + "'");
        }
    }

    private List<Row> readCsv(File f) throws Exception {
        List<Row> rows = new ArrayList<>();
        try (BufferedReader in = new BufferedReader(new FileReader(f, StandardCharsets.UTF_8))) {
            String line;
            while ((line = in.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("address")) {
                    continue;
                }
                String[] p = line.split(",");
                if (p.length < 4) {
                    printerr("skipping malformed row: " + line);
                    continue;
                }
                long addr = Long.decode(p[0].trim());
                String name = p[1].trim();
                boolean thumb = p[2].trim().equalsIgnoreCase("thumb");
                long size = Long.decode(p[3].trim());
                rows.add(new Row(name, addr, size, thumb));
            }
        }
        return rows;
    }

    // Phase 1: mode + disassembly + function. Analysis is deliberately NOT run here.
    private void createFunctions(List<Row> rows) throws Exception {
        ProgramContext ctx = currentProgram.getProgramContext();
        Register tmode = ctx.getRegister("TMode");
        if (tmode == null) {
            printerr("no TMode register: is the language ARM:LE:32:v4t?");
            return;
        }
        Disassembler dis = Disassembler.getDisassembler(currentProgram, monitor, null);
        FunctionManager fm = currentProgram.getFunctionManager();
        int created = 0;
        int renamed = 0;
        int failed = 0;

        for (Row r : rows) {
            Address start = toAddr(r.addr);
            Address end = toAddr(r.addr + Math.max(r.size, 2) - 1);
            try {
                ctx.setValue(tmode, start, end, BigInteger.valueOf(r.thumb ? 1 : 0));
                dis.disassemble(new AddressSet(start, start), new AddressSet(start, end), true);
            }
            catch (Exception e) {
                failed++;
                printerr("disassemble failed " + r.name + " @ " + start + ": " + e);
                continue;
            }
            Function f = fm.getFunctionAt(start);
            if (f != null) {
                if (!f.getName().equals(r.name)) {
                    f.setName(r.name, SourceType.USER_DEFINED);
                    renamed++;
                }
                continue;
            }
            AddressSet body = instructionRun(start, end);
            try {
                fm.createFunction(r.name, start, body, SourceType.USER_DEFINED);
                created++;
            }
            catch (Exception e) {
                failed++;
                printerr("createFunction failed " + r.name + " @ " + start + " body " + body + ": " + e);
            }
        }
        println("funcs: " + created + " created, " + renamed + " renamed, " + failed + " failed, " +
            "of " + rows.size() + " rows");
    }

    // The run of contiguous instructions that disassembly produced from `start` (stops at the
    // first byte disassembly did not cover, e.g. a literal pool).
    private AddressSet instructionRun(Address start, Address end) {
        Listing listing = currentProgram.getListing();
        AddressSet set = new AddressSet();
        Address a = start;
        while (true) {
            Instruction ins = listing.getInstructionAt(a);
            if (ins == null) {
                break;
            }
            Address ia = ins.getAddress();
            if (ia.compareTo(end) > 0) {
                break;
            }
            if (!set.isEmpty() && !ia.equals(set.getMaxAddress().add(1))) {
                break;
            }
            set.addRange(ia, ia.add(ins.getLength() - 1));
            a = ia.add(ins.getLength());
        }
        if (set.isEmpty()) {
            set.addRange(start, start);
        }
        return set;
    }

    // Phase 2: decompile and write the drafts.
    private void writeDrafts(List<Row> rows, File outDir) throws Exception {
        outDir.mkdirs();
        DecompInterface ifc = new DecompInterface();
        ifc.setOptions(new DecompileOptions());
        if (!ifc.openProgram(currentProgram)) {
            printerr("the decompiler refused this program");
            return;
        }
        FunctionManager fm = currentProgram.getFunctionManager();
        int written = 0;
        int noFunction = 0;
        int failed = 0;
        long bytes = 0;
        try {
            for (Row r : rows) {
                Address start = toAddr(r.addr);
                Function f = fm.getFunctionAt(start);
                if (f == null) {
                    noFunction++;
                    println("no function at " + r.name + " @" + start);
                    continue;
                }
                DecompileResults res = ifc.decompileFunction(f, 120, monitor);
                if (!res.decompileCompleted() || res.getDecompiledFunction() == null) {
                    failed++;
                    println("decompile failed " + r.name + ": " + res.getErrorMessage());
                    continue;
                }
                String c = res.getDecompiledFunction().getC();
                File out = new File(outDir, r.name + ".c");
                try (PrintWriter w = new PrintWriter(out, StandardCharsets.UTF_8)) {
                    w.print("/* Ghidra 12.1.4 decompiler DRAFT of " + r.name + " at 0x" +
                        String.format("%08X", r.addr) + " (" + (r.thumb ? "thumb" : "arm") +
                        ", " + r.size + " bytes).\n" +
                        " * NON-MATCHING: machine output, for reading the logic only (types, loops, branches).\n" +
                        " * It does not compile to the ROM's bytes with agbcc -- never paste it into src/funcs/.\n" +
                        " * Generated by scripts/ghidra_drafts.sh (Ghidra 12.1.4).\n" +
                        " */\n");
                    if (!c.endsWith("\n")) {
                        c = c + "\n";
                    }
                    w.print(c);
                }
                written++;
                bytes += c.length();
            }
        }
        finally {
            ifc.dispose();
        }
        println("drafts: " + written + " written, " + noFunction + " had no function, " + failed +
            " decompile failures, " + bytes + " C chars");
    }
}
