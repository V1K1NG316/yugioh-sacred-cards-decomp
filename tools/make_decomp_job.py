"""Queue one local job that decompiles one function into matching C (milestone Y5).

Usage:
  PY tools/make_decomp_job.py sub_080243A0            # queue it (after this tool is merged on main)
  PY tools/make_decomp_job.py sub_080243A0 --dry-run  # show the recipe and the make_job.py command

The job may change exactly one file, src/funcs/<name>.c, and its check is
`PY tools/match_func.py <name>`: the worker runs agbcc, links the result at the function's ROM
address and compares the bytes, so "done" cannot be claimed, only measured. Nothing is queued
here by itself -- run this tool when you mean it.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import romcode  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PY = 'C:/Users/USER/AppData/Local/hermes/hermes-agent/.hermes-runtime/python/cpython-3.11-windows-x86_64-none/python.exe'

RECIPE = """Write one C file that compiles with agbcc to exactly the ROM's bytes for the function
`{name}` at {addr} in Yu-Gi-Oh! The Sacred Cards (GBA). #1 is the ROM's own disassembly, #2 is the
style to copy, #4 is the only test that counts.

1. Read the disassembly: `D:/Yugioh_DeComp_V2/private/asm/funcs/{name}.s` (absolute path: your worktree has no private/asm).
   That path is for READING only. Write your C file ONLY inside your worktree:
   `D:/Yugioh_DeComp_V2/private/worktrees/<your job id>/src/funcs/{name}.c`. Never write into
   `D:/Yugioh_DeComp_V2/src/` (the main project): a file there fails the job.
   Lines starting with `@` are comments. `{name}: @ {addr}` is the function start. A line like
   `_08004758: .4byte 0x0201FCC0` is a literal pool word: the ROM loads that constant with
   `ldr rN, _08004758` and you must reproduce it without writing it yourself (see rule 3c).
   `.incbin` at the end of the file is data behind the function -- leave it alone, it is not yours.
   `bl sub_YYYYYYYY` calls another function; `ldr r0, _XXXXXXXX` reads a constant.
{draft}

2. Read the three functions already matched, they are the house style:
   `src/funcs/sub_0800AF94.c`, `src/funcs/sub_08004750.c`, `src/funcs/sub_08007604.c`.
   Also read `docs/decomp.md` (conventions) and `include/global.h` (u8/u16/u32).

3. Write `src/funcs/{name}.c`. That is the ONLY file you may change. Rules:
   a. It must contain `#include "global.h"` and define `{name}` with exactly that name, spelled the
      same as the file, no `static`.
   b. Call another ROM function by declaring it and calling it, e.g.
      `void sub_0800AF3C(void);` then `sub_0800AF3C();`. Never invent a helper name.
   c. A constant address the code reads or writes (ROM table, RAM variable) is written as a symbol
      whose name ends in its 8 hex digit address, exactly like agbcc does it itself:
      `extern u8 gUnk_0201FCC0[];` then `return gUnk_0201FCC0[3];`
      Do NOT write `*(u8 *)(0x0201FCC0 + 3)`: agbcc folds that into one pool constant and the
      bytes come out different. For a plain store the raw form is right when the value is simple:
      `*(u16 *)0x02020B34 = 0;`
   f. Plain C only: no `asm(...)`, no other functions or variables defined in the file; the check refuses them.
   d. A symbol whose name does not end in `_<8 hex digits>` cannot be resolved: the check refuses
      it. If you think you need one, stop and report instead.
   e. Match the shape: same number of instructions, same registers if you can, arguments read from
      r0/r1 and the result returned in r0.

4. Test: `PY tools/match_func.py {name}`
   - Exit code 0 and a line `MATCH {name} @ {addr}: N bytes identical` means you are done.
   - A `FAIL` line prints the first differing offset, both byte strings, and a side-by-side
     disassembly with the differing instructions marked. Read it: `rom` is the truth, `ours` is
     your C.
   - The END of the asm tells you the return type: `pop {{r0}}` + `bx r0` means the function returns
     NOTHING (`void`; r0 only carries the return address). `pop {{r1}}` + `bx r1` means it returns a
     value in r0. A callee whose result is unused can be declared `void`. Do not fight this rule.
     The same rule decides how you DECLARE a function you call: open its asm file
     (`D:/Yugioh_DeComp_V2/private/asm/funcs/<callee>.s`) and look at ITS end: `pop {{r0}}` = declare it `void`.
   - Common causes of a near miss: operands in the wrong order (`sub` vs reversed), a variable gcc
     can remove (write the expression in one go instead of storing to a temporary), signed vs
     unsigned (`ldrsb` vs `ldrb`), or an `if` gcc turns into a conditional move.
   - To see a near miss instruction by instruction, run `PY tools/diff_func.py <name>` (the same
     thing as `tools/diff_func.sh <name>`): the ROM's instructions on the left, yours on the right,
     differing lines marked. It builds exactly what the check builds, so the two never disagree.
   - The Ghidra draft uses `in_lr`, `undefined4`, `in_stack_...` and `SUB84`/`ZEXT` calls: those
     are Ghidra's own bookkeeping, not part of the function. Ignore them and trust the asm.
   - Do not run the permuter (a randomized C search) yourself: that is Hermes' job with
     `tools/permute_func.sh`, and a search score is not evidence. Your evidence is step 4.
   - If agbcc reports an error instead, the C does not compile; fix that first.
   - You may run the test as often as you like; it does not change any file.

5. Do not touch anything else. Not `config/`, not `tools/`, not `include/`, not `docs/`, and above
   all not `private/` (it holds the ROM and the generated disassembly; the harness reads them).
   Do not create extra files, not even a note -- put any remark in the job's report.

6. Commit EXACTLY this one file, with exactly these two commands (never `git add .`, `-A` or `-f`;
   JOB.json and RESULT.md must stay uncommitted):
   `git add src/funcs/{name}.c`
   `git commit -m "decompile {name}"`
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('name', help='function to decompile, e.g. sub_080243A0')
    ap.add_argument('--dry-run', action='store_true',
                    help='print the recipe and the make_job.py command; queue nothing')
    ap.add_argument('--max-attempts', type=int, default=2)
    a = ap.parse_args()

    rows = {n: (addr, ext, mode) for n, addr, ext, mode in romcode.read_functions(ROOT)}
    if a.name not in rows:
        sys.exit('%s is not in config/functions.csv' % a.name)
    addr, ext, mode = rows[a.name]
    if mode != 'thumb':
        sys.exit('%s is %s code; the harness only does THUMB' % (a.name, mode))
    if (ROOT / 'src' / 'funcs' / (a.name + '.c')).exists():
        sys.exit('src/funcs/%s.c already exists' % a.name)
    asm = ROOT / 'private' / 'asm' / 'funcs' / (a.name + '.s')
    if not asm.exists():
        sys.exit('%s is missing: run scripts/disasm.sh first' % asm)

    # Ghidra draft (Y5 tooling, [019]): a reading aid, never a source to copy.
    draft_c = ROOT / 'private' / 'ghidra' / (a.name + '.c')
    if draft_c.exists():
        draft = """\n   A decompiler DRAFT of this function is at `%s` (absolute path).\n   Read it to understand the logic -- its types, loops and branch conditions are useful. It is NOT\n   matching C: pasting it into your file will fail the check. Use the disassembly as the truth for\n   every instruction and the draft only as a hint about what the code is doing.""" % draft_c.as_posix()
    else:
        draft = ''

    text = RECIPE.format(name=a.name, addr='0x%08X' % addr, draft=draft)
    if len(text) > 6000:
        sys.exit('recipe is %d chars, make_job.py allows 6000' % len(text))

    draft = ROOT / 'private' / 'jobs' / 'drafts' / ('decomp_%s.md' % a.name)
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(text, encoding='utf-8', newline='\n')

    cmd = [PY, str(ROOT / 'tools' / 'make_job.py'),
           '--title', 'Decompile %s (0x%08X)' % (a.name, addr),
           '--kind', 'decompile',
           '--allowed', 'src/funcs/%s.c' % a.name,
           '--check', 'PY tools/match_func.py %s' % a.name,
           '--instructions-file', str(draft),
           '--max-attempts', str(a.max_attempts),
           '--created-by', 'deepseek']

    if a.dry_run:
        print('recipe written to %s\n' % draft)
        print(text)
        print('command (not run):\n  %s' % ' '.join(cmd))
        return 0
    import subprocess
    r = subprocess.run(cmd)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
