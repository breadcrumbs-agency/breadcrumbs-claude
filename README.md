# breadcrumbs-claude

The Claude Code adapter of breadcrumbs. It gives `identify` (the client name that means Claude Code) and `setup` (the line that adds the breadcrumbs MCP server to Claude Code), the source of its sessions for `ingest` and `sync` of breadcrumbs-common, and the ports for the viewers of breadcrumbs-spacegraph (the project where a session ran, the numbers of a session, the name of the store).

- Needs: breadcrumbs-common (and breadcrumbs-spacegraph for the viewers).
- Use: `python -m breadcrumbs core setup claude-code` prints the setup line. `python -m breadcrumbs ingest claude-code [PATH]` reads the stored sessions of Claude Code into one store (see `breadcrumbs_claude/sessions.py` for the files and the records that it reads). `python -m breadcrumbs --home ~/.claude/breadcrumbs sync claude-code [PATH]` reads the same sessions and puts each one in the memory of its project.
- Test: `PYTHONPATH=../breadcrumbs-common:. python -m unittest discover -s tests`.

MIT licence. Part of breadcrumbs-agency.

## One memory for each project

The memory of Claude Code is `~/.claude/breadcrumbs` (the base). `sync` puts each session where its folder (the cwd of the session) belongs, by `breadcrumbs/scope.py`: the project of a folder is its `.breadcrumbs` entry, else its git repository, else its source tree, else the folder itself. A project owns its memory, `~/.claude/breadcrumbs/scopes/<id>`; nothing is written into the project. A session that ran in no project (no folder, the home folder, a temporary folder, a folder that is gone, a `.breadcrumbs` file that says `off`) goes to the base. `BREADCRUMBS_SCOPE=off` puts every session there.

So one project never holds the sessions of another. The MCP server of the plugin runs in the folder where Claude Code runs, and a call that names no store looks only in the memory of that project (`stores` says where: `default`). To look further, name a store, or `*` for all of them.

`sync` is safe to run again and again: a session that has not changed adds nothing, a request is counted once, and each memory gets its `state.db` (time, tokens, project and branch of each session) for the viewers. A memory that was made by `ingest` before the scopes keeps its old copies; move it away and `sync` builds the new ones from the sessions of Claude Code.

## As a Claude Code plugin

The `release` branch is the plugin: this part plus the files of breadcrumbs-common and breadcrumbs-spacegraph under `lib/` (built by `breadcrumbs/tools/bundle.py`), so it needs no PyPI package. Needs Python 3.11 or newer (`BREADCRUMBS_PY` names one).

    /plugin marketplace add breadcrumbs-agency/breadcrumbs-claude#release
    /plugin install breadcrumbs@breadcrumbs-agency

Or from a clone of the `release` branch: `claude --plugin-dir /path/to/breadcrumbs-claude`. The `master` branch is the source of the part: it has no `lib/`, so the plugin files there run only inside a bundle. To build one from the folders beside this one: `python ../breadcrumbs/tools/bundle.py claude OUTDIR`, then `claude plugin marketplace add OUTDIR` and `claude plugin install breadcrumbs@breadcrumbs-agency`.

What it does:

| | |
|---|---|
| MCP server `breadcrumbs` | tools `find`, `open`, `zoom`, `trail`, `stores`, `health`, on the memory of the current project (`bin/bc-mcp`, then breadcrumbs-common's `launch-mcp.sh`, shared by every harness plugin) |
| hooks `SessionStart`, `SessionEnd` | `sync` in the background, one at a time, no output, never a failure (`bin/bc-sync`; `BREADCRUMBS_SYNC=off` turns it off) |
| `/breadcrumbs:viz` | `sync`, then the explorer of this project on 127.0.0.1 (read-only): the map of its sessions, Context, Measures (tokens, cache, by model, project and branch) and the calendar. In the browser, or in a cmux split |
| `bin/bc` | `python -m breadcrumbs` on the right Python, on the memory of the current project: `sh bin/bc find QUERY`, `sh bin/bc stats`, `sh bin/bc sync claude-code` |

The Size panel (the ACE folds) is empty: Claude Code has no ACE layer. The cost is not known per request, so the cost measures have no data.
