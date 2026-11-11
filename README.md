# breadcrumbs-claude

The Claude Code adapter of breadcrumbs. It gives `identify` (the client name that means Claude Code) and `setup` (the line that adds the breadcrumbs MCP server to Claude Code).

- Needs: breadcrumbs-common.
- Use: `python -m breadcrumbs core setup claude-code` prints the setup line.
- Test: `PYTHONPATH=../breadcrumbs-common:. python -m unittest discover -s tests`.

MIT licence. Part of breadcrumbs-agency.
