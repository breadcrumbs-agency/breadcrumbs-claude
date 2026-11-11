"""The adapter of the package breadcrumbs_claude: Claude Code gives its entry of the harness table of core.py.
ports.load() imports this module by the name of its package (breadcrumbs_*); no module imports it.
"""
import shlex

from breadcrumbs import ports

if ports.layer("claude", __file__):
    ports.harness("claude-code", "Claude Code", ("claude",), lambda cmd: "claude mcp add breadcrumbs -- " + shlex.join(cmd),
                  order=20)
