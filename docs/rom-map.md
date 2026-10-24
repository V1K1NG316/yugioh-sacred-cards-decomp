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
**A3 settled (2026-10-12, milestone Y5):** agbcc does reproduce ROM functions byte for byte. With
gcc 2.9-arm-000512 and pokefirered's flags (`-mthumb-interwork -Wimplicit -Wparentheses -Werror -O2
-fhex-asm`), three ROM functions match exactly — literal pool placement and the
`push {lr}` / `pop {r0}` / `bx r0` return included — and `make compare` stays byte-identical with
their C linked into the build. See `docs/decomp.md` §5 and approximation A3 in
`docs/approximations.md`.

## 4. Function census (verified: fixpoint of the Y3 disassembly)

`config/functions.csv`, header `address,name,mode,size,source`; **1977 rows**, sorted, unique:
1973 THUMB, 4 ARM (the startup stub of §2 plus `0x08036C74`). Lowest `0x08000000`, highest
`0x0803B5AC`. By `source` column:

| source | rows | what it means |
|---|---|---|
| `ptr_prologue` | 681 | target of an odd `0x08xxxxx1` pointer word whose head is a THUMB `push {…, lr}` |
| `bl_thumb` | 347 | target of a THUMB `BL` inside an accepted function |
| `disasm` | 943 | found by gbadisasm itself: a `BL` target the Y2 census could not see |
| `irq_table` | 2 | `0x08003B70`, `0x08003B94` (interrupt stubs, §2) |
| `reset_vector` / `reset_branch` / `crt0_writes_0x03007FFC` / `crt0_bx_literal_0x0800021C` | 1 each | the four entry points of §2 |

The Y2 seeds (`tools/find_functions.py`, §4 of the part-2 report) gave 1034 rows. The reason they
missed 943 is measurable: the finder's `BL` closure ran *inside* census extents, and an extent ends
at the first return, so a `BL` in the tail of a function (or in code only reachable through it) was
never walked ([011]). Y3 fixed that by taking the function list from the disassembly itself:
`scripts/disasm.sh` loops

```
config/functions.csv -> private/asm/rom.cfg -> gbadisasm -> rom_full.s -> functions_from_rom_s.py -> config/functions.csv
```

until the list stops changing (cap 5 loops). Real run, from scratch: loop 1 `1034 rows -> 1977` rows,
loop 2 `function list stable at 1977 rows`. Every address that was in the list stays in it
(a missing one is a hard error), so the loop only ever adds.

Where the 1034 Y2 rows came from (unchanged, still the evidence for A4/A6): the four entry points of
§2; the interrupt table at `0x0807F420` (`irq_table`); a whole-ROM sweep of 4-aligned words holding
an odd `0x08xxxxx1` ROM address (`ptr_prologue`: 833 candidates, 681 accepted, none refused by the
decode rule A4, **20 refused by the proximity rule A6** — all 20 in the data half, the nearest
312 660 bytes (`0x4C554`) from any BL-closure function while the furthest accepted one is 22 564
(`0x5824`) away); then BL closure over those (347 `bl_thumb` targets). The 20 rejected targets are
listed in REPORT `[008]`.

The one function the Y3 loop added that is **ARM** is `0x08036C74` (12 bytes, `source=disasm`) —
found through a Thumb→ARM interworking call, which confirms the [011] lead that ARM code hides in
this ROM (J0005, Claude's Thumb→ARM thunk scan, looks for the rest).

**Sizes (A5).** `size` is now the distance to the **next row's address**; the last row runs to the
sentinel `0x08FFFFFC`. The extents therefore tile the ROM by construction and are disjoint, and
`tools/test_functions_csv.py` still verifies disjointness independently. A data table or literal pool
between two functions belongs to the earlier row's extent — the extents are address ranges, not
"code only".

Checked by `tools/test_functions_csv.py` (exit 0): exact header; uniqueness, sorting, range;
alignment and unit-sized extents; the six entry addresses; `rows >= 1900`; **no overlapping
extents**; every `ptr_prologue` row really begins with `B5xx`; **every `bl_thumb` row is the target
of a THUMB `BL` whose own address lies inside the extent of another listed function**; and, when
`private/asm/rom_full.s` exists, **the CSV is exactly the function-start set of the generated
disassembly** (same addresses, names, modes — check 9, the fixpoint test, written independently of
`tools/functions_from_rom_s.py`).

**Still not a complete census.** The disassembler only decodes where the list, a `BL` or a pointer
table sends it, so code reached only by a computed jump stays data (A1/A2). The honest leftover is
now measurable: gbadisasm emitted no label at or above `0x0803B61C`, so everything from
`0x0803B61C` to the end of the ROM (16 533 984 bytes, 98.6 % of the ROM) is one unlabelled data run.
Nothing has yet proven there is no code in it — that is a Y2/Y3 open item, not a finding (A8).

## 5. Code/data map (verified: `tools/code_map.py` over the Y3 disassembly)

```
ROM: 16777216 bytes (0x08000000..0x09000000)
functions: 1977  (thumb 1973, arm 4)
data runs (.incbin): 243  16565922 bytes (98.74% of the ROM)
instructions + literal pools + padding: 211294 bytes (1.26% of the ROM)
code block: 0x08000000..0x0803B61C (243228 bytes) = everything before the first data run
            of 1048576 bytes or more (the bulk data tail)

data runs >= 4096 bytes inside the code block: 1
  0x0800D0E8-0x0800ED58    7280 B  valid THUMB (code-like)
```

So the game code is a **single block, `0x08000000`–`0x0803B61C`** (243 228 bytes, ~238 KiB), of which
211 294 bytes (86.9 %) are not `.incbin` data: instructions 177 622, `.4byte` pointer words 30 372
(7 593 words: 626 jump-table words plus 6 967 literal-pool words), `.align` padding 3 300. The
remaining 31 934 bytes of the block are labelled data (the 7 280-byte run below and smaller ones). The
rest of the ROM — 16 533 984 bytes, 98.6 % — is the bulk data tail.

Two things changed against the Y2 view of this section. First, "code bytes" no longer means the sum
of extents: with contiguous extents that sum *is* the ROM. The instruction/pool/padding number comes
from the disassembly instead (ROM − `.incbin` bytes). Second, the old per-gap table is not
reproducible: those gaps are now covered by real functions, and the data runs appear as many small
ones (a 4 KiB-plus region gets split wherever the disassembler has a label). One large run survives
inside the block, `0x0800D0E8` (7 280 B, THUMB-shaped bytes) — the same region the Y2 report listed as
"not code-like (table/data)", and what it really is remains open.

The 1 MiB data-block profile of §5 is unchanged by Y3 (identical numbers to the earlier run), so the
A7 table below still stands as a set of guesses:

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
wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash scripts/disasm.sh   # Y3, the fixpoint loop
wsl -d Ubuntu-24.04 --cd /mnt/d/Yugioh_DeComp_V2 -- bash -c 'make compare'
PY tools/test_functions_csv.py
PY tools/code_map.py
```

`docs/approximations.md` A1 (finder is a linear-scan heuristic), A2 (pointer-only targets skipped),
A3 (compiler guess), A4 (THUMB decode-validity rule), A5 (how `size` is derived), A6 (proximity rule
for pointer-table candidates), A7 (data-region guesses), A8 (what makes a data run "data").

## Which version this ROM is (Claude, 2026-10-12 19:56)
Our ROM (`rom/sacred_cards_usa.gba`, SHA-1 `d3710031…5230`, **CRC32 `BF7FBD2E`**, 16 MiB, code AY7E, header
checksum 09) is byte-identical to the V1 file named **"Yu-Gi-Oh! - The Sacred Cards (USA) (Early Days
Collection)"**, i.e. Konami's re-release, not the 2003 cartridge. Data Crystal lists CRC32 `141FB1CC` for the
original USA cartridge (same code/checksum), so the two builds differ somewhere. All extracted data and every page
describe the **Early Days Collection** build. Community sources (speedrunners often use original carts or mods)
are hypotheses only; verify everything against this ROM.

**Cart vs EDC, diffed 2026-10-24 (Claude, cart dump SHA-1 `a06735f9c3d10be9339657026981aef77af34b27`):** same size,
header and layout; 35,087 bytes differ in four areas. (1) Code: `sub_080195E8` at `0x080195F0`, the cart has a `bl`
(`eaf7b2fa`) where the EDC has `b` + nop (`0ae00000`), so the re-release skips one call. (2) `0x0809392C`-`0x08093989`:
one card name, "Space Megatron" in the cart, "Space Drone" in the EDC, all six languages. (3) `0x08D52274`-`0x08D54472`:
24 three-byte changes at 4-byte spacing in 12 clusters, not identified yet. (4) `0x08E95F00`-`0x08E9E937` (35 KB):
`0xFF` padding in the cart, data in the EDC. No other function differs, so matched C and extracted data hold for both.
