---
description: Open the breadcrumbs explorer on the memory of this project (map, calendar, measures)
allowed-tools: Bash
---
Bring the memory up to date, then open the explorer of this project:

1. Run `sh "${CLAUDE_PLUGIN_ROOT}/bin/bc" sync claude-code`. It reads the sessions of Claude Code, each into the memory of the git repository or folder where it ran, and prints one JSON line (its `stores` list has the sessions of each memory). It takes a few seconds.
2. Run `sh "${CLAUDE_PLUGIN_ROOT}/bin/bc" viz` from the current folder. It starts the read-only explorer for the memory of this project on 127.0.0.1 and opens it in the browser (or a cmux split), and prints the address.

Then tell me, in two lines: which project this is and how many sessions its memory holds (the entry of `stores` whose `scope` is this folder or its git repository; the `scope` is empty for the default memory), and the address of the explorer. If a step fails, show its error and stop.
