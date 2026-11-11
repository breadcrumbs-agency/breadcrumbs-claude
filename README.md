# breadcrumbs-claude

The Claude Code adapter of breadcrumbs. It gives `identify` (the client name that means Claude Code) and `setup` (the line that adds the breadcrumbs MCP server to Claude Code), and the source of its sessions for the ingest of breadcrumbs-common.

- Needs: breadcrumbs-common.
- Use: `python -m breadcrumbs core setup claude-code` prints the setup line. `python -m breadcrumbs ingest claude-code [PATH]` reads the stored sessions of Claude Code into the store (see `breadcrumbs_claude/sessions.py` for the files and the records that it reads).
- Test: `PYTHONPATH=../breadcrumbs-common:. python -m unittest discover -s tests`.

MIT licence. Part of breadcrumbs-agency.
