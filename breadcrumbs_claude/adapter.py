"""The adapter of the package breadcrumbs_claude: Claude Code gives its entry of the harness table of core.py.
ports.load() imports this module by the name of its package (breadcrumbs_*); no module imports it.

    harness   claude-code: identify, setup, the source of the ingest and of `sync` (sessions.py), its usage, its icon
              and its project links (the repository, and the site the other harnesses link to)
    ports     state codebase profile  (for the viewers of breadcrumbs-spacegraph: the numbers of a session that `sync` wrote
              to state.db, the project where it ran, and the name of the store; Claude Code has no ACE log, no hidden
              sessions and no price table here)

The memory of Claude Code is ~/.claude/breadcrumbs (the base), and `sync` puts each session in the memory of its project
under it (breadcrumbs/sync.py): the git repository or folder where the session ran.

icon.png is the Claude mark (Simple Icons, CC0) in cream on the terracotta of the Claude app icon, 96 px: the viewers draw
it beside the brand. The name and the mark belong to Anthropic; they say which program a view shows.
"""
import os

from breadcrumbs import ports, scope, statedb, sync

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


def _add_scopes(sub):
    p = sub.add_parser("scopes", help="the projects of the base memory, each with its own memory; --here PATH: the "
                                      "scopes that hold PATH")
    p.add_argument("--here", default=None, metavar="PATH", help="the scopes of PATH, nearest first, instead of the list")


def _scopes(args, home):
    """`scopes`: the projects of the base memory with their memories, as Hermes's `scopes` lists them. `home` is the
    memory the command opens (the project of the current folder under BREADCRUMBS_HERE); its base holds the scopes."""
    base = scope.base_of(home)
    if args.here:
        here = os.path.abspath(os.path.expanduser(args.here))
        used = sync.project(here, sync.enabled(), base=base)  # the project that `sync` puts a session of this folder in
        if not used:
            print("%s: no project (a temporary folder, the home folder, a folder that is gone, or BREADCRUMBS_SCOPE=off): "
                  "the default memory" % here)
            return 0
        print("here   %s  (%s)  memory %s" % (scope.short(used[1]), used[0],
                                             scope.short(scope.store_home(base, used[1]))))
        for kind, root in scope.chain(here, exclude=sync.no_project(base)):
            if root != used[1]:
                print("above  %s  (%s)" % (scope.short(root), kind))
        return 0
    got = scope.known(base)
    for s in got:
        print("%-8s %-9s %s  (%s)%s" % ("memory" if s["present"] else "empty", s["kind"], scope.short(s["root"]), s["id"],
                                         "" if os.path.isdir(s["root"]) else "  [folder gone]"))
    if not got:
        print("no scope has a memory yet (a session in a git repository starts one)")
    return 0


if ports.layer("claude", __file__):
    ports.give("state", statedb.read)
    ports.give("codebase", _codebase)
    ports.give("profile", lambda home: NAME)
    ports.harness("claude-code", "Claude Code", ("claude",), ports.mcp_add("claude"), order=20, source=_source,
                  usage=_usage, icon=ports.image(__file__, "icon.png"),
                  repository="https://github.com/breadcrumbs-agency/breadcrumbs-claude",
                  pages="https://breadcrumbs-agency.github.io/hermes-breadcrumb-plugin/")
    ports.command("scopes", _add_scopes, _scopes, after="vault")
