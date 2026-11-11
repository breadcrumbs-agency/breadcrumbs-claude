"""The adapter of the package breadcrumbs_claude: Claude Code gives its entry of the harness table of core.py.
ports.load() imports this module by the name of its package (breadcrumbs_*); no module imports it.
"""
from breadcrumbs import ports

if ports.layer("claude", __file__):
    ports.harness("claude-code", "Claude Code", ("claude",), ports.mcp_add("claude"), order=20)
