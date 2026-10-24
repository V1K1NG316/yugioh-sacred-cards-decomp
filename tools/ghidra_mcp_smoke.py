#!/usr/bin/env python3
"""Smoke test for the Ghidra MCP server (scripts/ghidra_mcp_server.sh start).

Talks MCP to the bridge at http://127.0.0.1:8081/mcp with the official MCP SDK
client over streamable-http -- i.e. exactly the way an agent client connects --
and exercises four calls:

  1. list_tools                      -- the bridge is serving a tool catalog
  2. find_functions                  -- list functions in the loaded program
  3. get_functions                   -- decompile sub_08006BE4 (one real function)
  4. get_xrefs_to                    -- who references the duel table 0x08D35C28
  5. rename_variables                -- rename a local of sub_08006BE4 in a
                                        throwaway COPY of the analysed project
                                        (our real project is closed first and
                                        reopened last, so its symbols are never
                                        touched by this test)

Run inside WSL from the repo root, with the server up:
  ./private/venv/bin/python tools/ghidra_mcp_smoke.py

Exit 0 = every step answered as expected. Nothing here is a substitute for a real
matching-C check; it only proves the pipe works end to end.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

REPO = Path(__file__).resolve().parent.parent
REAL_PROJECT_DIR = REPO / "private" / "ghidra" / "project"
COPY_DIR = REPO / "private" / "tmp" / "ghidra-mcp-smoke"
PROGRAM = "baserom.gba"
FUNCTION = "sub_08006BE4"
FUNCTION_ADDR = "0x08006BE4"
DUEL_TABLE = "0x08D35C28"

failures: list[str] = []


def ok(step: str, detail: str) -> None:
    print(f"PASS  {step}: {detail}")


def bad(step: str, detail: str) -> None:
    failures.append(step)
    print(f"FAIL  {step}: {detail}")


def text_of(result) -> str:
    """Flatten a CallToolResult into text (the bridge answers in plain text or JSON)."""
    parts = []
    for item in getattr(result, "content", []) or []:
        parts.append(getattr(item, "text", "") or "")
    return "\n".join(p for p in parts if p)


async def call(session: ClientSession, tool: str, args: dict) -> tuple[bool, str]:
    try:
        result = await session.call_tool(tool, args)
    except Exception as exc:  # protocol-level failure (unknown tool, HTTP error)
        return False, f"{type(exc).__name__}: {exc}"
    body = text_of(result)
    if getattr(result, "isError", False):
        return False, body or "(error with no message)"
    return True, body


async def run(url: str) -> int:
    print(f"connecting to {url}")
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1 -- the catalog. The bridge starts lazy (full catalog is past the
            # function-declaration limit of some providers): core groups are
            # listing/function/program; xref and headless are pulled in here.
            listing = await session.list_tools()
            names = [t.name for t in listing.tools]
            ok("list_tools", f"{len(names)} tools advertised: {', '.join(sorted(names)[:8])} ...")
            wanted = ("find_functions", "get_functions", "rename_variables")
            missing = [t for t in wanted if t not in names]
            if missing:
                bad("list_tools", f"core tools missing: {missing}")

            good, body = await call(session, "load_tool_group", {"group": "xref"})
            good2, body2 = await call(session, "load_tool_group", {"group": "headless"})
            if good and good2:
                ok("load_tool_group(xref)", " ".join(body.split())[:160])
                ok("load_tool_group(headless)", " ".join(body2.split())[:160])
            else:
                bad("load_tool_group", (body + body2)[:300])
            listing = await session.list_tools()
            names = [t.name for t in listing.tools]
            missing = [t for t in ("get_xrefs_to", "open_project", "close_project")
                       if t not in names]
            if missing:
                bad("load_tool_group", f"still missing after load: {missing}")
            else:
                ok("tools after load", f"{len(names)} advertised, incl. get_xrefs_to/open_project/close_project")

            # 2 -- functions
            good, body = await call(session, "find_functions", {"limit": 5})
            if good:
                head = " ".join(body.split())[:220]
                ok("find_functions", head)
                total = None
                for token in body.replace(",", " ").split():
                    if token.startswith("total"):
                        total = token
                print(f"      (function list headline: {total or 'no total field'})")
            else:
                bad("find_functions", body[:300])

            # 3 -- decompile one known function
            good, body = await call(session, "get_functions",
                                    {"function": FUNCTION, "fields": "decompiled_code"})
            if good and ("void" in body or "{" in body):
                code = "\n".join(line for line in body.splitlines() if line.strip())[:400]
                ok("get_functions", f"{FUNCTION} decompiled, {len(body)} chars; first lines:\n"
                                    + "\n".join("      | " + line for line in code.splitlines()[:6]))
            else:
                bad("get_functions", body[:300])

            # 4 -- xrefs to the duel table
            good, body = await call(session, "get_xrefs_to", {"address": DUEL_TABLE})
            if good:
                ok("get_xrefs_to", f"{DUEL_TABLE}: " + " ".join(body.split())[:220])
            else:
                bad("get_xrefs_to", body[:300])

            # 5 -- rename a local, in a throwaway copy of the project
            if COPY_DIR.exists():
                shutil.rmtree(COPY_DIR)          # only ever this path, under private/tmp
            COPY_DIR.mkdir(parents=True)
            copy_project = COPY_DIR / "project"
            shutil.copytree(REAL_PROJECT_DIR, copy_project)
            print(f"      copied {REAL_PROJECT_DIR} -> {copy_project}")

            good, body = await call(session, "close_project", {})
            if good:
                ok("close_project (before the copy)", " ".join(body.split())[:160])
            else:
                bad("close_project", body[:200])

            good, body = await call(session, "open_project", {"path": str(copy_project / "AY7E.gpr")})
            if good:
                ok("open_project (throwaway copy)", " ".join(body.split())[:160])
            else:
                bad("open_project (throwaway copy)", body[:300])
                return 1

            good, body = await call(session, "open_program", {"path": PROGRAM})
            if not good:
                bad("open_program (throwaway copy)", body[:300])

            # The decompiler names its locals in the C it prints (puVar1, uVar4, ...);
            # get_functions' locals list is filled only for some functions, so read
            # the name out of the draft the decompiler wrote.
            good, body = await call(session, "get_functions",
                                    {"function": FUNCTION, "fields": "locals,decompiled_code"})
            old_name = ""
            if good:
                print(f"      locals field: {' '.join(body.split())[:200]}")
                code = body
                try:
                    code = json.loads(body).get("decompiled_code") or body
                except json.JSONDecodeError:
                    pass
                match = re.search(r"\b([A-Za-z_]\w*(?:Var|Stack)_?\d*)\b", code)
                old_name = match.group(1) if match else ""
                print(f"      local chosen from the draft: {old_name or '(none found)'}")
            else:
                bad("get_functions (locals)", body[:300])

            if not old_name:
                bad("rename_variables", "no local variable name found to rename")
            else:
                new_name = "smoke_renamed_local"
                good, body = await call(session, "rename_variables",
                                        {"function": FUNCTION_ADDR,
                                         "variable_renames": {old_name: new_name}})
                if good and (new_name in body or '"success":true' in "".join(body.split())):
                    ok("rename_variables", f"{FUNCTION} {old_name} -> {new_name}: "
                                           + " ".join(body.split())[:200])
                else:
                    bad("rename_variables", (body or "no confirmation")[:300])
                # read it back
                good, body = await call(session, "get_functions",
                                        {"function": FUNCTION, "fields": "decompiled_code"})
                if good and new_name in body:
                    ok("rename verified", f"{new_name} appears in the decompiled {FUNCTION} of the copy")
                else:
                    bad("rename verified", "renamed name not visible after the rename")

            # put the real project back
            good, body = await call(session, "close_project", {})
            good, body = await call(session, "open_project", {"path": str(REAL_PROJECT_DIR / "AY7E.gpr")})
            if good:
                ok("open_project (real project restored)", " ".join(body.split())[:160])
            else:
                bad("open_project (real project restored)", body[:300])
            good, body = await call(session, "open_program", {"path": PROGRAM})
            if not good:
                bad("open_program (real project)", body[:300])

    print()
    if failures:
        print(f"SMOKE TEST FAILED: {len(failures)} step(s): {', '.join(failures)}")
        return 1
    print("SMOKE TEST PASSED: every step answered (catalog, functions, decompile, xrefs, rename in a copy)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8081/mcp",
                        help="MCP bridge endpoint (default: the loopback bridge)")
    args = parser.parse_args()
    return asyncio.run(run(args.url))


if __name__ == "__main__":
    sys.exit(main())
