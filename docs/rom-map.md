# ROM map — Yu-Gi-Oh! The Sacred Cards (GBA, USA, `AY7E`)

Milestone Y2, part 1 (entry, compiler evidence, first function census) and part 2 (function-pointer
seeds, extents/sizes, code/data map). Written 2026-10-12 by DeepSeek.
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

Evidence collected this turn (counts are from the part-1 census of 158 functions; the census is now
1034 — see §4 — the return-idiom split below was not recomputed, so treat 155 as a sample):

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

`config/functions.csv`, header `address,name,mode,size,source`; **1034 rows**, sorted, unique:
1031 THUMB, 3 ARM (exactly the startup stub of §2). Lowest `0x08000000`, highest `0x0803B5AC`.
By `source` column:

| source | rows | what it means |
|---|---|---|
| `ptr_prologue` | 681 | target of an odd `0x08xxxxx1` pointer word whose head is a THUMB `push {…, lr}` |
| `bl_thumb` | 347 | target of a THUMB `BL` inside an accepted function |
| `irq_table` | 2 | `0x08003B70`, `0x08003B94` (interrupt stubs, §2) |
| `reset_vector` / `reset_branch` / `crt0_writes_0x03007FFC` / `crt0_bx_literal_0x0800021C` | 1 each | the four entry points of §2 |

Seeds, in the order the finder uses them:

1. the four entry points of §2;
2. the interrupt table at `0x0807F420` (`irq_table`);
3. a whole-ROM sweep of 4-aligned words holding an odd `0x08xxxxx1` ROM address (`ptr_prologue`):
   833 such words were found, 681 targets were accepted, **none** were refused by the decode rule
   (A4) and **20 were refused by the proximity rule** (A6). All 20 sit in the data half of the ROM;
   the nearest is 312 660 bytes (`0x4C554`) away from any BL-closure function, and the furthest
   *accepted* one is 22 564 bytes (`0x5824`) away — a two-order-of-magnitude separation, not a
   tuned threshold. The 20 rejected targets are listed in REPORT `[008]`.
4. BL closure over everything accepted so far: 347 new `bl_thumb` targets. **A BL target is
   accepted without any decode filter** — a real function need not begin with a prologue (the
   interrupt stubs at `0x08003B94` are a single `bx lr`).

**Sizes (A5).** `size = min(walk_end, next_function_start) - address` where `walk_end` is where the
linear walk stopped: past the last instruction it visited (a return, an unconditional branch, or the
16 KiB cap). Bounding by the next function start keeps extents disjoint by construction, and
`tools/test_functions_csv.py` verifies disjointness independently.

Checked by `tools/test_functions_csv.py` (exit 0): exact header; uniqueness, sorting, range;
alignment and unit-sized extents; the six entry addresses; `rows >= 1000`; **no overlapping
extents**; every `ptr_prologue` row really begins with `B5xx`; and **every `bl_thumb` row is the
target of a THUMB `BL` whose own address lies inside the extent of another listed function**. The
last one replaces the part-1 check, which counted `BL`-shaped halfwords anywhere in the ROM (data
included) and so accepted almost any even address ([006] finding 2). It is falsifiable: adding a
fake row `0x080FFF00,sub_080FFF00,thumb,4,bl_thumb` to the CSV makes the check exit 1
(`FAIL 0x080FFF00 bl_thumb: no THUMB BL into it from inside another extent`).

**Still not a complete census.** 26 pointer values reached only through `ldr rX,[pc,#imm]` + `bx rX`
are not walked into (A2); 3 of them are now in the census anyway because a *table* word also points
at them. Whether every real function start is present is **unverified** — the finder only knows
entry points, interrupt stubs, BL targets and prologue-shaped pointer targets, and it cannot see
code reached only by a computed jump (A1).

## 5. Code/data map

`tools/code_map.py` (read-only report over `config/functions.csv` + the ROM):

```
ROM: 16777216 bytes (0x08000000..0x09000000)
functions: 1034  code bytes: 64170 (0.38% of the ROM)
code region: 0x08000000..0x0803B5D0 (26.39% of it is function extents)
```

So the game code is a **single block, `0x08000000`–`0x0803B5D0`** (243 152 bytes, ~237 KiB), of which the finder
accounts for 64 170 bytes (26.4%) in function extents; the rest of the block is literal pools,
padding between functions, and the tables below. Not one accepted function lies above
`0x0803B5AC` — the 20 pointer-shaped words pointing higher were rejected by A6.

Gaps larger than 4 KiB **inside** the code block (bytes at the gap start, classified):

| gap | size | first bytes look like |
|---|---|---|
| `0x08004318`–`0x080058AC` | 5524 B | valid THUMB — code the finder missed (A1/A6 leads) |
| `0x0800D0DE`–`0x0800ED58` | 7290 B | not code-like (table/data) |
| `0x080145AA`–`0x08015B08` | 5470 B | not code-like (table/data) |
| `0x0801A5EE`–`0x0801E940` | 17234 B | not code-like (table/data) |
| `0x08031DA4`–`0x08033D64` | 8128 B | valid THUMB — code the finder missed (A1/A6 leads) |

The two "valid THUMB" gaps are the honest leftovers: ~13.6 KiB of code-shaped bytes that no seed,
BL or accepted pointer table reaches. They are leads for a later job, not part of the census.

First cut at the data half — 1 MiB blocks after the code end (A7, all guesses):

| block | zero | ASCII | odd ROM-pointer words | guess |
|---|---|---|---|---|
| `0x08100000` | 53.1% | 17.1% | 308 | mixed tables + padding (A7) |
| `0x08200000` | 61.8% | 12.1% | 730 | mostly padding + tables (A7) |
| `0x08300000` | 14.5% | 30.9% | 1484 | tables + text (A7) |
| `0x08400000` | 25.0% | 18.3% | 772 | mixed data (A7) |
| `0x08500000` | 21.8% | 12.5% | 250 | mixed data (A7) |
| `0x08600000`–`0x08800000` | ~2% | ~36% | ~700 | long ASCII runs — text block (A7) |
| `0x08900000` | 18.8% | 31.4% | 1844 | tables + text (A7) |
| `0x08A00000` | 4.9% | 12.9% | 1653 | dense binary (graphics?) (A7) |
| `0x08B00000` | 2.0% | 14.6% | 1728 | dense binary (graphics?) (A7) |
| `0x08C00000` | 15.2% | 14.9% | 1310 | mixed data (A7) |
| `0x08D00000` | 3.6% | 67.8% | 2941 | text-heavy block (card text?) (A7) |
| `0x08E00000` | 0.3% | 54.9% | 21 | text, no pointers (A7) |
| `0x08F00000` | 1.3% | 0.2% | 1 | raw binary, no text, no pointers (A7) |

The `J0002` ASCII-string dump (`private/extracted/strings.txt`, 57 622 runs) is the dataset that
can turn the A7 guesses into facts; the job passed on 2026-10-12 06:14 and its output lands in
`private/`, which is not part of this branch.

## 6. How to reproduce

```
wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/dis_range.sh 0x080000C0 0x08000200
PY tools/find_functions.py && PY tools/test_functions_csv.py
PY tools/code_map.py
```

`docs/approximations.md` A1 (finder is a linear-scan heuristic), A2 (pointer-only targets skipped),
A3 (compiler guess), A4 (THUMB decode-validity rule), A5 (how `size` is derived), A6 (proximity rule
for pointer-table candidates), A7 (data-region guesses).
