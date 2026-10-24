# Matching C (milestone Y5)

How a function goes from "bytes in the ROM" to "C that compiles back to those exact bytes", and
what every tool in that loop does. Owner of the tools: Hermes on DeepSeek; they are the standard
way to hand work to the local model (`tools/make_decomp_job.py`).

## 1. The loop

```
tools/pick_decomp_targets.py 10      # pick small unmatched THUMB functions
tools/make_decomp_job.py <name>      # queue one as a local job (after the harness is on main)
       ... local model writes src/funcs/<name>.c ...
tools/match_func.py <name>           # the check: exit 0 only on an exact byte match
scripts/build_matched.sh             # run by `make compare`; puts the C back into the ROM build
tools/progress.py                    # how much of the ROM is C now
```

`make compare` is still the gate: it stops being a Y3-only test the moment a C file exists, because
`build_matched.sh` replaces that one function's generated asm with the compiled code, and the
build is byte-identical only if the C is right.

## 2. `tools/match_func.py <name>`

1. Finds `<name>` in `config/functions.csv` (main checkout): address, mode, extent (A5).
2. Copies `src/funcs/<name>.c` from **this** checkout (a job worktree counts) into
   `private/build/match/<name>.<pid>/` in the main checkout, and runs `scripts/match_func.sh` there:
   `cpp -nostdinc -undef -std=gnu89 -I private/tools/agbcc/include -I private/tools/agbcc -I
   include` → `agbcc -mthumb-interwork -Wimplicit -Wparentheses -Werror -O2 -fhex-asm` →
   `arm-none-eabi-as -mcpu=arm7tdmi -mthumb-interwork`.
   That is pokefirered's agbcc invocation minus its charmap preprocessor.
   The assembling step is `scripts/asm_with_defsyms.sh`: every undefined symbol whose name ends in
   `<8 hex digits>` is defined as that absolute address, so a constant the C names
   (`extern u8 gUnk_0201FCC0[]`) settles into the object as the ROM's own constant instead of a
   relocation. That is what `make` does for the same file (`.set gUnk_0201FCC0, 0x0201FCC0` in
   `scripts/build_matched.sh`), and it is what lets §9 compare assembly text without tripping over
   toolchain bookkeeping. Calls to another function keep their relocation.
   The build directory is per run (`<name>.<pid>`) and is deleted when the run ends, so two runs at
   once — a local job's check beside `make compare` — cannot collide; `--keep` and `--workdir`
   change that (tools/diff_func.py uses both). `scripts/build_matched.sh` is the one caller that
   still uses the shared `private/build/match/<name>`.
3. Links the object at the function's address (`scripts/link_at.sh`) and compares
   `.<size>` bytes — gcc's own `.size`, so the literal pool is included — with the ROM's bytes at
   that address. Length must not pass the next function's start.
4. Exit 0 = `MATCH ... N bytes identical`. Exit 1 = `FAIL`, with the first differing offset, both
   byte strings, and a side-by-side disassembly where the differing instructions are marked.
   Exit 2/3/4 = usage, compile or link problem (the tool prints what the toolchain said).

Symbol resolution: an undefined symbol whose name ends in `_<8 hex digits>` is an address in this
ROM (`sub_08001234`, `gUnk_03001234`, `data_08123456`); anything else is refused, because guessing
would make the check meaningless. A symbol that is a THUMB function row in `config/functions.csv`
is defined as a `.thumb_func`; anything else is a plain data label at that address with no Thumb
bit. Refused outright: ARM functions (need `agbcc_arm`), a function that needs `.data`/`.rodata`
(it would live at a second address), and any symbol without the address suffix.

**Why stubs and not `ld --defsym`**: an absolute symbol tells the linker the callee is ARM code,
so a Thumb `bl` to it gets an interworking veneer inserted and the call bytes come out wrong
(measured: `bl 800afa0 <__sub_0800AF3C_from_thumb>` instead of the ROM's direct `bl`). Each
symbol therefore gets a two-byte stub in a section of its own, placed at its real address by a
generated linker script.

## 3. Conventions for `src/funcs/<name>.c`

- One function per file, the file name is the symbol name; `#include "global.h"` for `u8/u16/u32`.
- Calls: declare the callee (`void sub_0800AF3C(void);`) and call it. No invented helper names.
- A constant address is a *symbol* ending in its address, which is also what agbcc itself does
  (it writes `.word gUnk_02020B34`, never `.word 0x02020B34`):
  `extern u8 gUnk_0201FCC0[];` … `return gUnk_0201FCC0[3];`
  The raw form `*(u8 *)(0x0201FCC0 + 3)` does **not** match: agbcc folds the `+3` into the pool
  word (`0x0201FCC3`) where the ROM loads `0x0201FCC0` and uses `ldrb r0, [r0, #3]`.
  A simple store is fine raw: `*(u16 *)0x02020B34 = 0;`.
- `s32`, `bool32` and the rest of `include/global.h` are there when a function needs them; extend
  that header, not the individual files.

## 4. The three functions matched so far

| C | address | bytes | shape |
|---|---|---|---|
| `sub_08004750.c` | `0x08004750` | 12 | `return gUnk_0201FCC0[3];` (literal pool) |
| `sub_08007604.c` | `0x08007604` | 12 | `*(u16 *)0x02020B34 = 0;` (pool + `strh`) |
| `sub_0800AF94.c` | `0x0800AF94` | 10 | `sub_0800AF3C();` (call + `pop`/`bx` return) |

## 5. The compiler (settles approximation A3)

All three matched **exactly** with agbcc at `-O2` and pokefirered's flags, including the literal
pool placement and the `push {lr} … pop {r0}; bx r0` return. The banner agbcc prints is
`@ Generated by gcc 2.9-arm-000512 for Thumb/elf`. A3 guessed an "old GNU/agbcc-class" compiler
and ruled out only ARM's `armcc`; the decisive test A3 itself named is now done — see
`docs/rom-map.md` §3.

## 6. How the C gets into the build (`scripts/build_matched.sh`)

For every `src/funcs/<name>.c`, `make compare` first rewrites **that one file**
`private/asm/funcs/<name>.s` (generated, never edited by hand) as: the compiled code, then
`.space` zero padding up to the function's extent (A5). Two traps, both measured:

- **Syntax.** `rom.s` is `.syntax unified`; agbcc writes *divided* syntax, where `mov r0, #0x0` is
  the 2-byte `movs`. Read as unified it silently becomes the 4-byte `mov.w`, and the function grows
  2 bytes (this is how the first build came out 4 bytes too long). The fragment is therefore
  bracketed with `.syntax divided` … `.syntax unified`.
- **Local labels.** agbcc's `.L3`/`.Lfe1` are per-assembly-file, so two matched functions collide
  inside one `rom.s`; they are renamed to `.L<name>_3` etc.

Each function is then re-assembled *alone* (`private/build/match/<name>/shim.s`: macros include,
`.syntax unified`, `.text`, the fragment), linked at its address, and compared with the ROM over
the whole extent — before `make compare` runs. Only if that passes does the C end up in the ROM,
and then the whole-ROM SHA-1 decides.

## 7. Limits

- Only THUMB. The 4 ARM functions in the CSV are out of scope for now.
- A function that needs a `.data`/`.rodata` section (string literals, tables) is refused: such
  bytes belong at a second ROM address, which this harness cannot place yet.
- "Matched" means: the ROM's bytes over the function's extent are exactly what this C compiles to,
  plus zero padding up to the extent (asserted, not assumed). Extents are A5, i.e. they include
  whatever sits between two functions, so a non-zero tail would make the build fail loudly.
- The extent (A5) is not a proven function length. A C body that is too short but is followed by
  zero bytes in the ROM would pass; nothing has seen that case yet.

## 8. Ghidra decompiler drafts (`scripts/ghidra_drafts.sh`)

`tools/match_func.py` decides pass/fail; Ghidra only helps a writer understand what a function
*means*. It runs headless (no GUI, no licence prompt) on `private/baserom.gba`:

1. `scripts/ghidra_setup.sh` (once) downloads the Java runtime and Ghidra into `private/tools/`,
   checking each file against the SHA-256 its project publishes.
2. `scripts/ghidra_drafts.sh` imports the ROM as raw binary, language `ARM:LE:32:v4t` at
   `0x08000000`, and for every row of `config/functions.csv` sets the CPU mode (`TMode` 0 = ARM,
   1 = THUMB), disassembles from that address and creates a function named as the CSV names it —
   so a call to another known function reads `sub_080243A0`, not `FUNC_080243a0`.
   `tools/ghidra/GbaDecompDrafts.java` does that (`funcs` mode); the analysis pass is deliberately
   *after* it, because Ghidra's own analysis assumes ARM everywhere and would disassemble the THUMB
   code the wrong way first.
3. The same script then decompiles each of those functions and writes `private/ghidra/<name>.c` —
   a **draft**. Its own header says so: types, loops and branch conditions are useful, but the C is
   machine output and does not compile to the ROM's bytes with agbcc. The disassembly stays the
   truth for every instruction.
4. Re-runs reuse the analysed project in `private/ghidra/project/`; `--only <name>` decompiles a
   single function without re-importing or re-analysing (seconds, not minutes).

`tools/make_decomp_job.py` quotes the draft's absolute path in a job's recipe when the file exists,
with the same warning: read it, do not copy it. The recipe also says what a draft's `in_lr`,
`undefined4` and `in_stack_...` are: Ghidra's own bookkeeping, to be ignored.

## 9. Near misses: `tools/diff_func.sh`, `tools/permute_func.sh`

Two tools for the case the check says `FAIL` and the C is *almost* right. Both need the community
tools in `private/tools/` and the Python in `private/venv/` (§10).

**`tools/diff_func.sh <name>`** (the real file is `tools/diff_func.py`; same arguments and the same
view of the world as `tools/match_func.py`, a job worktree's `src/funcs` included) builds
`src/funcs/<name>.c` exactly as the check does, builds the ROM's own bytes for that function as a
second object (`scripts/rom_func_obj.sh`, which verifies them against the ROM) and prints the two
side by side with [asm-differ](https://github.com/simonlindholm/asm-differ):

```
TARGET                                                   CURRENT (10)
0:    ldr     r0, [pc, #4]  @ =0x0201fcc0 (8)            0:    ldr     r0, [pc, #4]  @ =0x0201fcc3 (8)
2:    ldrb    r0, [r0, #3]                        i      2:    ldrb    r0, [r0, #0]
4:    bx      lr                                         4:    bx      lr
6:    .short  0x0000                                     6:    .short  0x0000
8:    .word   0x0201fcc0                          |      8:    .word   0x0201fcc3
```

Left column: the ROM, the truth. Right column: our C. `i` marks an instruction whose operands
differ, `|` marks a line that is missing on one side, and the number in `CURRENT (n)` is how many
lines differ — `(0)` means the function matches and there is nothing to fix. Both objects are
assembled through `scripts/asm_with_defsyms.sh` (§2), so a constant the C names by a symbol and the
ROM's inline constant read the same and are not reported as differences.

**`tools/permute_func.sh <name> [minutes] [--base file.c] [--jobs N]`** sets up
`private/permuter/<name>/` (the ROM's bytes as `target.o`, the C as `base.c`, a generated
`compile.sh` that is the harness pipeline, `run.log`) and runs
[decomp-permuter](https://github.com/simonlindholm/decomp-permuter) for that many minutes (default
5, `--stop-on-zero`). The best candidate it produced is copied to
`private/permuter/<name>/best.c` — **never** into `src/`. A score is a hint, not evidence: a
score-0 candidate still has to pass `tools/match_func.py` before anyone copies it in. Local jobs
never run the permuter.

Measured example (the demo both tools were built with, `sub_08004750`, 2026-10-12): the function is
`return gUnk_0201FCC0[3];`, deliberately perturbed into a pointer form —

```c
extern unsigned char gUnk_0201FCC0[];

unsigned char sub_08004750(void)
{
    unsigned char *p = &gUnk_0201FCC0[3];
    return *p;
}
```

That C is a near miss of exactly the kind §3 warns about: agbcc folds the `+3` into the literal
pool (`.word 0x0201FCC3` with `ldrb r0, [r0, #0]`) where the ROM has `.word 0x0201FCC0` with
`ldrb r0, [r0, #3]`. Permuter base score 10; `diff_func` shows those two lines.
`tools/permute_func.sh sub_08004750 5 --base <that file>` found a score-0 candidate in **3 seconds**
(119 candidates in the re-run and 170 in the first one — the workers race, so the count varies; the
wall clock includes building `target.o`):

```c
extern unsigned char gUnk_0201FCC0[];

unsigned char sub_08004750(void)
{
    int new_var;
    unsigned char *p;
    new_var = 3;
    return *(&gUnk_0201FCC0[new_var]);
}
```

and `tools/match_func.py sub_08004750` on it reports `MATCH ... 12 bytes identical`. The winner is
ugly — a dead variable survives, because agbcc folds it away and the bytes come out right — so it
is a *hint* for a human/agent to tidy up, then check again. The same run also showed that a signed
element type can be invisible: `extern signed char gUnk_0201FCC0[]`, returned as `unsigned char`,
compiles to the ROM's `ldrb` byte-for-byte (base score 0), because gcc 2.9 drops the sign-extending
load when the value is used as an unsigned char.

## 10. Setting the two community tools up

`bash scripts/decomp_tools.sh` (once) clones both tools into `private/tools/` at pinned
commits and installs their Python dependencies into `private/venv/`. If the distro's `python3` has
no pip and no usable venv seed, pip is bootstrapped into the venv itself from
`bootstrap.pypa.io/get-pip.py` (Arch's python has pip, so it is not needed there). Nothing is
installed system-wide, nothing under `private/` is committed; the commit hashes, sizes and licences
are in `docs/credits.md`. Without them, `diff_func`/`permute_func` say what is missing and stop.

## 11. Open: agbcc saves `lr` where the ROM does not (leaf + conditional branch)

Found 2026-10-12 while drafting 20 functions ([045]); it blocked J0030 (`sub_080045C4`) twice and
three of those drafts. Symptom: every instruction matches the ROM except the prologue/epilogue --
agbcc emits `push {lr}` ... `pop {r1}; bx r1` where the ROM has neither `push` nor `pop`, just
`bx lr` (2 bytes longer, and the literal pool then needs no `align` pad).

Counted over `private/asm/rom_full.s` (1971 THUMB functions): **82** are leaf functions with at
least one conditional branch and **no** `lr` save in the ROM; **177** others of the same kind do
save `lr`, so the ROM's compiler decided per function, while our agbcc (gcc 2.9-arm-000512,
`private/tools/agbcc`) saves `lr` for every source shape tried:

- 10 hand-written shapes (if/else two returns, reversed condition, index vs pointer, ternary, `while`,
  store inside/after the branch, `u16`/`u32`/pointer argument, `-O0/-O1/-O2`, `-f(no-)omit-frame-pointer`,
  with/without `-mthumb-interwork`) -- all `push {lr}` (`private/tmp/frames*.sh`).
- `tools/permute_func.sh sub_080045C4 5 --base private/tmp/rescue/sub_080045C4.c`: 41719 candidates,
  base score 405, nothing better, no `best.c`.
- Two probes written from the ROM's own disassembly (`sub_080045C4`, `sub_08018618`) reproduced the
  ROM's instruction bytes exactly -- same registers, same pool placement, same branch offsets -- and
  differed only by the frame.

So this looks like a difference in agbcc's Thumb "does this function need `lr`" heuristic (a far-branch
estimate made before the literal pools exist), not a source-shape problem; the class of affected
functions cannot be matched with the current toolchain until that is settled. Cheapest first moves:
match one of the 82 with a patched/candidate agbcc build, or list them as non-matching (asm) in
`config/functions.csv` and skip them in local jobs.




## Compiler: old_agbcc (settled by Claude, 2026-10-12 19:26)
The game was built with **old_agbcc** (the older agbcc build pokefirered ships as `tools/agbcc/bin/old_agbcc`).
Evidence: `sub_080045C4` (J0030) compiles to the exact ROM bytes with old_agbcc, while agbcc adds a
`push {lr}` / `pop {r0}; bx r0` frame the ROM lacks (the "lr heuristic" class from [045], ~82 leaf functions).
All 27 functions matched before the switch match with both compilers (tested one by one). Pilot drafts with
old_agbcc: sub_08008B74 33 → 3 bytes off, sub_0801351C 32 → 18, sub_080144C8 40 → 25.
`scripts/match_func.sh` / `permute_func.sh` now default to old_agbcc (override: `AGBCC=agbcc`).
