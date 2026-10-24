# Yu-Gi-Oh! The Sacred Cards — matching decompilation (GBA)

Reverse engineering **Yu-Gi-Oh! The Sacred Cards** (GBA, USA, the *Early Days Collection* build): a rebuild that
matches the original ROM byte for byte, documented game data, and, step by step, C code that compiles to the
game's exact bytes. Owner: Matter_Scatter.

**This repository contains no ROM and no game data.** You need your own legally obtained copy of the game
(SHA-1 `d3710031520d9cdae70d870c60b1667285fe5230`). Everything derived from the ROM (disassembly, extracted text and
tables, builds) is generated locally into `private/`, which is never committed (`tools/guard_repo.py` enforces it).

**How it is made:** an AI team. Claude directs and reviews; Hermes on DeepSeek drafts and does the hard analysis;
check scripts and Claude reviewer agents verify every change before it is committed. Rules are in `AGENTS.md`; the
pilot results are in `docs/pilot.md`. The first phase (2026-10-12 to 2026-10-14, on Windows with a local Qwen model
doing bulk work) is archived in `docs/archive/windows-v2/`, including its day-to-day log `AI_Conversation.md`.
Machine-specific paths use the placeholder `USER`.

## Milestones
| ID | Goal | Status |
|----|------|--------|
| Y0 | Repo, guards, hashes, agent scripts | done |
| Y1 | Shell build that rebuilds the exact ROM (`make compare`) | done |
| Y2 | Map of the ROM: code, data, libraries, compiler (old_agbcc) | done |
| Y3 | Disassembly split into ~1,977 functions, still byte-identical | done |
| Y4 | Card names/stats/passwords, text, duel decks and prize pools decoded | mostly done (card pictures open) |
| Y5 | Functions rewritten in C that compile to the same bytes | in progress: see `src/funcs/` |

## Building (WSL, Ubuntu 24.04)
Put your ROM at `rom/sacred_cards_usa.gba`, copy it to `private/baserom.gba`, generate the disassembly with
`bash scripts/disasm.sh`, then `make compare` (needs agbcc/old_agbcc and binutils for arm-none-eabi; see
`docs/decomp.md` and `docs/tools.md`).
