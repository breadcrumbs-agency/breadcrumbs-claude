---
description: Show which memory this folder uses (its project scope) and the scopes of the base memory
allowed-tools: Bash
---
Show the memory of this folder:

1. Run `sh "${CLAUDE_PLUGIN_ROOT}/bin/bc" scopes`. It prints the scopes of the base memory (`~/.claude/breadcrumbs`): one line for each project (a git repository, or a folder with a `.breadcrumbs` entry), with its memory's folder and its session count. The default memory has an empty scope.
2. Find the scope of the current folder: the project whose git repository or folder contains it (the nearest one). If none matches, the folder uses the default memory.

Then tell me, in two lines: the project of this folder (or `default`), and the memory folder that `find` and `open` read. If the command fails, show its error and stop. Do not change any file.
