"""The adapter of the package breadcrumbs_claude: Claude Code gives its entry of the harness table of core.py.
ports.load() imports this module by the name of its package (breadcrumbs_*); no module imports it.

    harness   claude-code: identify, setup, the source of the ingest and of `sync` (sessions.py), its usage and its icon
    ports     state codebase profile  (for the viewers of breadcrumbs-spacegraph: the numbers of a session that `sync` wrote
              to state.db, the project where it ran, and the name of the store; Claude Code has no ACE log, no hidden
              sessions and no price table here)

The memory of Claude Code is ~/.claude/breadcrumbs (the base), and `sync` puts each session in the memory of its project
under it (breadcrumbs/sync.py): the git repository or folder where the session ran.

icon.png is the Claude mark (Simple Icons, CC0) in cream on the terracotta of the Claude app icon, 96 px: the viewers draw
it beside the brand. The name and the mark belong to Anthropic; they say which program a view shows.
"""
from breadcrumbs import ports, statedb, sync

NAME = "claude"  # the profile: the one program whose sessions these memories hold


def _source(path):
    from . import sessions
    return sessions.sessions(path)


def _usage(path):
    from . import sessions
    return sessions.usage(path)


def _codebase(folder):
    found = sync.project(folder, sync.enabled())
    return found[1] if found else None


if ports.layer("claude", __file__):
    ports.give("state", statedb.read)
    ports.give("codebase", _codebase)
    ports.give("profile", lambda home: NAME)
    ports.harness("claude-code", "Claude Code", ("claude",), ports.mcp_add("claude"), order=20, source=_source,
                  usage=_usage, icon=ports.image(__file__, "icon.png"))
