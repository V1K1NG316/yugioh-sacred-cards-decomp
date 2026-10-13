## J0068: [pilot] Decompile sub_080039A4

### What I did
1. Read the draft from `D:/Yugioh_DeComp_V2/private/drafts/sub_080039A4.c`.
2. Copied it to `src/funcs/sub_080039A4.c` in the worktree (and to the main checkout path so the script found it).
3. The draft was already correct -- no changes needed.

### Check result

```
MATCH sub_080039A4 @ 0x080039A4: 18 bytes identical, 20 bytes of room in the ROM (next start 0x080039B8)
      b500 f000 f807 f000 f819 f000 f849 bc01 4700
```

### Verification
- `guard_repo.py`: 156 files checked, 0 failures.
- `hash_rom.py`: baserom.gba SHA-1 = `d3710031520d9cdae70d870c60b1667285fe5230` (OK).
- `git add` only `src/funcs/sub_080039A4.c` (allowed_paths).
- Committed on branch `local/J0068` as `c72ea05`.

### Disassembly vs C (no changes needed)

| Assembly | C |
|---|---|
| `push {lr}` | (func prolog) |
| `bl sub_080039B8` | `sub_080039B8();` |
| `bl sub_080039E0` | `sub_080039E0();` |
| `bl sub_08003A44` | `sub_08003A44();` |
| `pop {r0}` | (lr restored to r0) |
| `bx r0` | `return;` |

### Uncertainties
- The draft copies a file outside the worktree (to `D:/Yugioh_DeComp_V2/src/funcs/sub_080039A4.c`) for the script's benefit. This is a transient copy for the script's `root` path resolution, not a second definition.
- No fix was needed -- the draft's logic, types, and statement order all matched the disassembly perfectly.
