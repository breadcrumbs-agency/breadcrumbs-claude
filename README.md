# breadcrumbs-claude

The Claude Code adapter of breadcrumbs. It gives `identify` (the client name that means Claude Code) and `setup` (the line that adds the breadcrumbs MCP server to Claude Code), and the source of its sessions for the ingest of breadcrumbs-common.

- Needs: breadcrumbs-common.
- Use: `python -m breadcrumbs core setup claude-code` prints the setup line. `python -m breadcrumbs ingest claude-code [PATH]` reads the stored sessions of Claude Code into the store (see `breadcrumbs_claude/sessions.py` for the files and the records that it reads).
- Test: `PYTHONPATH=../breadcrumbs-common:. python -m unittest discover -s tests`.

MIT licence. Part of breadcrumbs-agency.

## As a Claude Code plugin

The `release` branch is the plugin: this part plus the files of breadcrumbs-common under `lib/` (built by `breadcrumbs/tools/bundle.py`), so it needs no PyPI package. It starts the breadcrumbs MCP server (tools `find`, `open`, `zoom`, `trail`, `stores`, `health`). Needs Python 3.11 or newer (`BREADCRUMBS_PY` names one).

    /plugin marketplace add breadcrumbs-agency/breadcrumbs-claude#release
    /plugin install breadcrumbs@breadcrumbs-agency

Or from a clone of the `release` branch: `claude --plugin-dir /path/to/breadcrumbs-claude`.
The `master` branch is the source of the part: it has no `lib/`, so the plugin files there run only inside a bundle.
