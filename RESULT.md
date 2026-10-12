# J0021 — RESULT.md

## What I did

Decompiled `sub_0800AFC4` at 0x0800AFC4. The function is 10 bytes: pushes lr, calls `sub_0800AF3C`, then pops r0 and branches through it (returning to the caller via the link register).

Written file: `src/funcs/sub_0800AFC4.c` — defines `sub_0800AFC4` as void returning, calls `sub_0800AF3C()`.

## How I figured it out

The disassembly (`sub_0800AFC4.s`) shows:
- `push {lr}` at +0
- `bl sub_0800AF3C` at +2
- `pop {r0}` at +6  
- `bx r0` at +8

The Ghidra draft confirms the logic: return the link register. The return type started as `u32` (matching Ghidra's `undefined4`) and the compiler produced bytes `bc02 4708` (pop {r1}, bx r1). Switched to `void` — agbcc then generated `bc01 4700` (pop {r0}, bx r0) which matches the ROM exactly.

## Check result

```
MATCH sub_0800AFC4 @ 0x0800AFC4: 10 bytes identical, 12 bytes of room in the ROM (next start 0x0800AFD0)
b500 f7ff ffb9 bc01 4700
```

## Assumptions

- The disassembly is the truth for every instruction; the Ghidra draft was used only for understanding the return mechanism.
- Changed return type from `u32` to `void` because agbcc's Thumb convention for void functions uses r0 for the return register.
