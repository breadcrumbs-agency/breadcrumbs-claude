"""The adapter of breadcrumbs_claude: it gives the entry 'claude-code' of the harness table of core.py (identify and setup).
Run with breadcrumbs-common and this folder on PYTHONPATH."""
import unittest

from breadcrumbs import harness_case


class Adapter(harness_case.HarnessCase):
    KEY, LABEL, LAYER = "claude-code", "Claude Code", "claude"
    NAMES = ['claude-code', 'Claude Code']
    SETUP = "claude mcp add breadcrumbs -- env PYTHONPATH=/x python -m breadcrumbs core mcp"


if __name__ == "__main__":
    unittest.main()
