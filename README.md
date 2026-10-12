# Yugioh_DeComp_V2

Reverse engineering **Yu-Gi-Oh! The Sacred Cards** (GBA, USA) for Matter_Scatter's private use: a rebuild that
matches the original cartridge byte for byte, then readable names, documented game data and, step by step, C code.

**Who works on it:** Claude directs and reviews; Hermes on DeepSeek Flash does the hard engineering (paid, so used
sparingly); Hermes on the local Qwen model does the bulk work for free, around the clock; scripts and Claude critics
check everything. Live progress: `STATUS.md`. The day-to-day log: `AI_Conversation.md`. Rules: `AGENTS.md`.

## Milestones
| ID | Goal | What Matter_Scatter can do with it | Status |
|----|------|-------------------------------------|--------|
| Y0 | Repo, guards, hashes, agent scripts | — | done |
| Y1 | Shell build that rebuilds the exact ROM | proves the tools work | next |
| Y2 | Map of the ROM: code, data, libraries, compiler | see what's where in the game | not started |
| Y3 | Disassembly split into named functions | browse the game's code | not started |
| Y4 | Card list, text, decks, graphics extracted | read the card database, edit text later | not started |
| Y5 | Functions rewritten in C that compile to the same bytes | real decompiled source | not started |
