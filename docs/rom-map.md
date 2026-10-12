# ROM map — Yu-Gi-Oh! The Sacred Cards (GBA, USA, `AY7E`)

Milestone Y2, part 1 (entry, compiler evidence, first function census). Written 2026-10-12 by DeepSeek.
Scope of this document: what was **observed** in `private/baserom.gba` (SHA-1
`d3710031520d9cdae70d870c60b1667285fe5230`, 16777216 bytes) with `scripts/dis_range.sh`, and what is still
unverified. Everything below marked "unverified" is a lead, not a fact.

## 1. Header (verified)
| Field | Value | Evidence |
|---|---|---|
| Title | `YUGIOH DM7` | ROM 0x00A0 (`0x080000A0`) |
| Game code | `AY7E` | 0x00AC (bytes `AY7EA4`) |
| Maker | `A4` | 0x00B0 |
| Fixed value | `0x96` | 0x00B2 |
| Save type string | `SRAM_V112` | ROM offset 0x176698 (`0x08176698`), one occurrence |
| Software version | 0 | byte 0x00BC |
| Complement check | `0x09` — matches the standard `-(0x19 + sum(0xA0..0xBC)) & 0xFF` | byte 0x00BD, computed: sum=`0x4DE` → `0x09` |
| File size | 16777216 bytes (16 MiB) | `os.path.getsize` (the header has no size field) |

## 2. Entry path (verified, instruction by instruction)

`scripts/dis_range.sh 0x08000000 0x08000010` (ARM):

```
 8000000: ea00002e  b 0x80000c0          <- reset vector, ARM, branches to crt0
```

`scripts/dis_range.sh 0x080000C0 0x08000200` (ARM) — crt0, **ARM mode**:

```
 80000c0: e3a00012  mov r0, #18         ; CPSR mode = IRQ
 80000c4: e129f000  msr CPSR_fc, r0
 80000c8: e59fd028  ldr sp, [pc, #40] @ 0x80000f8   ; sp_irq = 0x03007FA0
 80000cc: e3a0001f  mov r0, #31         ; CPSR mode = system
 80000d0: e129f000  msr CPSR_fc, r0
 80000d4: e59fd018  ldr sp, [pc, #24] @ 0x80000f4   ; sp_sys = 0x03007F00
 80000d8: e59f1138  ldr r1, [pc, #312] @ 0x8000218  ; r1 = 0x03007FFC
 80000dc: e28f0018  add r0, pc, #24                 ; r0 = 0x080000FC
 80000e0: e5810000  str r0, [r1]                    ; install IRQ handler pointer
 80000e4: e59f1130  ldr r1, [pc, #304] @ 0x800021c  ; r1 = 0x08016929
 80000e8: e1a0e00f  mov lr, pc
 80000ec: e12fff11  bx  r1                          ; -> main, THUMB (pointer is odd)
 80000f0: eafffff2  b   0x80000c0                    ; restart loop
```

Literal pool (ARM, 0x08000218-0x08000220): `0x03007FFC`, `0x08016929`, `0x0807F420`.

* **crt0 = `0x080000C0` (ARM).** This is the standard GBA dev-kit crt0: set the IRQ stack
  (`0x03007FA0`), set the system stack (`0x03007F00`), write the interrupt handler address to
  `0x03007FFC`, then `bx` into the C entry point and loop.
* **IRQ handler = `0x080000FC` (ARM).** Reached because crt0 stores `0x080000FC` at `0x03007FFC`.
  It reads `REG_IF` (`0x04000202`) and `REG_IE` (`0x04000200`), matches the lowest set bit,
  indexes a handler table at `0x0807F420`, calls the handler with `bx r0`, acknowledges the
  interrupt, restores `SPSR` and returns with `bx lr` at `0x08000214`.
* **Interrupt table = `0x0807F420`** (read by the dispatcher at `0x080001DC`):
  `word[0] = 0x08003B71` and `word[1..13] = 0x08003B95` — so the default handler is
  `0x08003B70` (THUMB) and every real interrupt handler is `0x08003B94` (THUMB).
* **`main` = `0x08016928` (THUMB)**, entered through the odd pointer `0x08016929`:
  `80016928: b510 push {r4, lr}` … `80016934: f01f f8c4 bl 0x8035ac0` … and it ends
  `80016980: bc10 pop {r4}` / `80016982: bc02 pop {r1}` / `80016984: 4708 bx r1`.

Everything else in the ROM is reached from these four entry points (plus the two handlers above).

## 3. Compiler (finding + one labelled guess)

Evidence collected this turn:

1. **Mixed mode.** Of the 158 function starts found so far, **155 are THUMB and 3 are ARM**, and the
   3 ARM ones are exactly the startup stub (`reset`, `crt0`, `irq_handler`). All C code is THUMB.
   The startup jumps into THUMB C through an odd pointer (`0x08016929`), the normal interworking
   idiom.
2. **THUMB return idiom is `bx`, not `pop {.., pc}`.** Of the 155 THUMB functions, 85 end with a
   `pop {…}` followed by `bx rN` (e.g. `main`: `bc10` `bc02` `4708`), 27 end with `pop {…}; bx lr`,
   35 end with an unconditional branch (tail call), and only **1** ends with `pop {…, pc}`.
   The `pop`/`bx` pair is the shape produced by GNU-style THUMB code generation.
3. **The game talks to the BIOS directly**, through its own one-instruction wrappers, instead of a
   C library, e.g. `0x0803692C: df0b svc 11 (CpuSet)` / `4770 bx lr`, `0x08036930: df13 svc 19`,
   `0x08036934: df11 svc 17`.
4. **No library startup/veneer signatures found so far:** no run of ARM `_call_via_r0..r3` veneers
   (26 scattered ARM `bx rN` words, never four in a row), and no `__divsi3`/`__udivsi3`/`__modsi3`
   shaped helper among the 158 functions. How division is done is still **undetermined**.

**Finding (evidence: 1-3):** the ROM is a mixed-mode build — ARM startup stub identical to the GBA
dev-kit crt0/intr, everything else THUMB C with `pop`/`bx` returns and direct BIOS calls.
**Guess A3 (docs/approximations.md):** the C was built by an old GNU/agbcc-class THUMB compiler
rather than by ARM's own `armcc` (whose returns use `pop {…, pc}`). Not proven; the decisive test is
to compile one ROM function with `agbcc` and compare bytes (`make compare` territory, milestone Y5).

## 4. Function census (verified output of `tools/find_functions.py`)

`config/functions.csv`, header `address,name,mode,source`; 158 rows, sorted, unique:
155 THUMB, 3 ARM. Lowest `0x08000000`, highest `0x0803B5AC`.
Checked by `tools/test_functions_csv.py` (exit 0): header, uniqueness, sorting, range, alignment,
the four step-1 entry points, row count >= 150, and for 20 fixed-seed random THUMB rows that a real
THUMB `BL` in the ROM targets the address (32440 `BL` targets found over the whole ROM).

Sources: `reset_vector`, `reset_branch`, `crt0_writes_0x03007FFC`, `crt0_bx_literal_0x0800021C`,
`irq_table_entry`, `bl_thumb`, `bl_arm`, `blx_thumb` (the `source` column).

**Coverage is deliberately conservative and is NOT a complete function list.** 13 further targets
were seen only as pointer values loaded from a literal pool; they were not walked into (A2). Two
known gaps: the region `0x080064C8`-`0x08016800` and most of the ROM above `0x0803B5AC` contain
plausible code (e.g. the instruction sequence at `0x08010000` is valid THUMB) that no `BL` from the
158 functions reaches, i.e. it is reached through jump tables / function-pointer tables. Growing this
census (pointer tables, whole-ROM `BL` sweep, prologue detection) is the next Y2 step.

**Unverified beyond this point:** whether `0x0803B5AC` is the real end of the code region; whether the
code region continues above it in another block; the sizes of the functions (only starts are recorded).

## 5. How to reproduce

```
wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/dis_range.sh 0x080000C0 0x08000200
PY tools/find_functions.py && PY tools/test_functions_csv.py
```

`docs/approximations.md` A1 (finder is a linear-scan heuristic), A2 (pointer-only targets skipped),
A3 (compiler guess).
