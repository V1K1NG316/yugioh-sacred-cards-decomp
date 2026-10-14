# Research: recent GBA decompilations (Claude, 2026-10-14, at Matter_Scatter's request)

Source: the awesome-decomp-games list (GBA "Decompilations" marked 100%) and each project's GitHub README / API.
Read as information only. Nothing below is copied code; it is what their READMEs say about method.

| Project | Matching? | Compiler | Notable tooling | Repo created → last push |
|---|---|---|---|---|
| GT Advance 3 (722rsr/gtadv3-decomp) | yes, full ROM byte-for-byte | **pinned old_agbcc** (same as ours) | objdiff, decomp.dev, mGBA bindings, function census | 2026-10-07 → 2026-10-13 (30 commits; work likely began earlier, privately) |
| Kirby: Nightmare in Dream Land (overjt/knidl) | yes | agbcc family, pinned in Docker | objdiff report, decomp.dev, mGBA boot test, **shift test**, asset extract/rebuild | 2026-08-20 → 2026-10-05 (~7 weeks, 972 commits) |
| Kingdom Hearts: CoM (Pheenoh/khcom) | yes | agbcc | **configure.py + ninja** build, `decomp.yaml`, asset extractor | 3,167 commits |
| Klonoa: Empire of Dreams (testyourmine/kleod) | badges only | not stated | decomp.yaml, asmdiff, calcrom | 136 commits |

None of the READMEs says how much AI was used. The pace (Kirby: a full matching decomp in ~7 weeks) is in line
with our own 1–2 month estimate.

## What "100%" means there
- GT Advance 3: 100% of the **identified C functions**, measured in emitted bytes ("not source readability").
- Kirby: 100% of **code**, but 0.49% stays assembly **by design** (ROM header, crt0, BIOS call stubs); data is
  labelled `.incbin` structure, typed only where a decompiled function proves the layout; 4,937 of 5,348 functions named.

## Ideas worth adopting here (ranked)
1. **Incremental build (ninja / objdiff-style per-function objects).** Our `make compare` rebuilds every matched
   function every time (~10 min at 754 functions). Cache per function → seconds. Biggest immediate win.
2. **Function census** (GT Advance 3): scan the code for function prologues (`push {..., lr}`) and cross-check the
   function list. Fixes our A35 problem (unlisted functions hidden inside extents) and gives the true total.
3. **Shift test** (Kirby): build the ROM with everything moved by some bytes and check it still boots. Proves no
   hard-coded addresses remain → mods can grow functions (today an edited function must fit its old space).
4. **Asm by design** for header/crt0/BIOS stubs: count them as done; do not spend permuter time on them.
5. **Evidence-backed names** (Kirby `renames.csv`) + named constants: the route for moving Track B's names into the
   matching source (Track A) with proof, instead of guesses.
6. **objdiff + decomp.dev**: the community-standard progress page and per-function diff view.
