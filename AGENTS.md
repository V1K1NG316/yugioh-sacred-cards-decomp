# AGENTS.md — rules for agents in this repo

Owner: **Matter_Scatter** (not a programmer; use they/them; plain language). Since 2026-10-24 the project runs on
the owner's Arch Linux PC and follows the owner's shared agent workflow, which lives in their private notes vault:
Claude Code directs and reviews, Hermes on DeepSeek does the heavy work from written task briefs, Claude reviewer
subagents check it, and only Claude Code commits. Task briefs, handoffs and lessons learned live in the vault, not
here. The old Windows setup (local Qwen job queue, PowerShell runners, `AI_Conversation.md` as the message log) is
archived in `docs/archive/windows-v2/` as a read-only record.

## Hard rules
1. `rom/sacred_cards_usa.gba` is the read-only original: the **Early Days Collection** build, SHA-1
   `d3710031520d9cdae70d870c60b1667285fe5230` (`config/yugioh.sha1`). Work from `private/baserom.gba`.
   The 2003 cart (CRC32 `141FB1CC`) differs in one call in `sub_080195E8`, one card name and some data (`docs/rom-map.md`).
2. **No game-derived file in git**: ROM, saves, generated disassembly, extracted graphics/text/tables, builds. They
   live in `private/`. Git holds authored files only. `.gitignore` is a whitelist: check new files with
   `git check-ignore -q <file>; echo $?` (0 = ignored). `tools/guard_repo.py` checks the index.
3. Write only inside this repo. No system-wide installs and no `sudo`: give the owner the command.
4. **Numbers, not vibes.** Every claim comes with the command and its real output. Times come from `date`.
5. A check must exit 0 only when the work is right. Before trusting a new check, feed it wrong work and see it fail.
6. Don't commit or push unless you are Claude Code. The public GitHub copy is published only after review, and never
   with anything game-derived in it.

## Gates (run before reporting; say "not run" for any gate you skipped)
1. `python3 tools/guard_repo.py` → 0 failures.  2. `python3 tools/hash_rom.py` → exit 0.
3. `make compare` → `private/build/yugioh.gba: OK`.  4. `git check-ignore -q` on every new file.

## Where things are
- `docs/decomp.md`: the matching-C loop and its tools. `docs/rom-map.md`, `docs/game-data.md`: what is known about the ROM.
- `docs/approximations.md`: every labelled guess (A1..An). `MODLOG.md`: dated log of changes with commands and output.
- `config/functions.csv`: the function list. `src/funcs/<name>.c`: matched functions, one per file.
- `tools/`, `scripts/`: generators, checks and build steps. `ops/`: the old Windows runners (to be replaced).
