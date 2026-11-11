"""The adapter of breadcrumbs_claude: it gives the entry 'claude-code' of the harness table of core.py (identify and setup).
Run with breadcrumbs-common and this folder on PYTHONPATH."""
import json
import unittest

from breadcrumbs import core, ports


class Adapter(unittest.TestCase):
    CMD = ["env", "PYTHONPATH=/x", "python", "-m", "breadcrumbs", "core", "mcp"]

    def setUp(self):
        self.entry = ports.harnesses()['claude-code']

    def test_the_package_gives_one_entry_to_the_table(self):
        self.assertEqual(self.entry["label"], 'Claude Code')
        self.assertEqual(ports.layer("claude", __file__), False)  # the adapter announced its layer once

    def test_identify_tells_the_client_names_apart(self):
        for name in ['claude-code', 'Claude Code']:
            self.assertEqual(core.identify(name), 'claude-code', name)
        for name in ("curl", "", None):
            self.assertEqual(core.identify(name), "unknown", name)

    def test_the_table_lists_it_in_its_place(self):
        self.assertIn('claude-code', core.harnesses())

    def test_setup_is_the_mcp_add_line_of_the_cli(self):
        self.assertEqual(self.entry["setup"](self.CMD), 'claude mcp add breadcrumbs -- env PYTHONPATH=/x python -m breadcrumbs core mcp')

    def test_health_counts_the_calls_of_this_harness(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            c = core.Core(core.Stores(root=tmp))
            try:
                c.call("stores", harness='claude-code')
                self.assertEqual(c.call("health")["calls"], {'claude-code': 1, "unknown": 1})
            finally:
                c.close()


if __name__ == "__main__":
    unittest.main()
