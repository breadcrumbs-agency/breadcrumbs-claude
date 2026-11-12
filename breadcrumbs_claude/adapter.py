"""The adapter of the package breadcrumbs_claude: Claude Code gives its entry of the harness table of core.py.
ports.load() imports this module by the name of its package (breadcrumbs_*); no module imports it.
"""
from breadcrumbs import ports


def _source(path):
    from . import sessions
    return sessions.sessions(path)


def _usage(path):
    from . import sessions
    return sessions.usage(path)


if ports.layer("claude", __file__):
    ports.harness("claude-code", "Claude Code", ("claude",), ports.mcp_add("claude"), order=20, source=_source,
                  usage=_usage)
