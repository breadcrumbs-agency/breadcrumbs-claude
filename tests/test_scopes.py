"""`scopes` for Claude Code: the projects of the base memory, each with its own memory, and `--here PATH` (the project that
`sync` puts a session of PATH in, then the folders above it). /breadcrumbs:scope runs it. The folders are made in a
temporary home; the temporary-folder exclusion of sync is patched off, because the test folders live under the system
temporary folder. Nothing is read from the real ~/.claude. Run with breadcrumbs-common and this folder on PYTHONPATH."""
import argparse
import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from breadcrumbs import ports, scope, sync

from breadcrumbs_claude import adapter


def run(base, here=None):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = adapter._scopes(argparse.Namespace(here=here), base)
    return code, out.getvalue()


class Scopes(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = os.path.realpath(tmp.name)
        self.base = os.path.join(self.tmp, ".claude", "breadcrumbs")
        self.repo = os.path.join(self.tmp, "work", "kettle")
        os.makedirs(os.path.join(self.repo, ".git"))
        os.makedirs(os.path.join(self.repo, "src"))
        patch = mock.patch.object(sync, "no_project", return_value=[])
        patch.start()
        self.addCleanup(patch.stop)

    def test_with_no_memory_yet_it_says_so(self):
        code, text = run(self.base)
        self.assertEqual(code, 0)
        self.assertIn("no scope has a memory yet", text)

    def test_a_scope_with_no_index_is_listed_as_empty_and_with_one_as_memory(self):
        scope.ensure(self.base, "git", self.repo)
        _, text = run(self.base)
        self.assertIn("empty    git", text)
        self.assertIn(scope.short(self.repo), text)
        self.assertIn("(%s)" % scope.scope_id(self.repo), text)
        open(os.path.join(scope.store_home(self.base, self.repo), "index.db"), "w").close()
        _, text = run(self.base)
        self.assertIn("memory   git", text)

    def test_here_names_the_project_sync_uses_and_its_memory(self):
        scope.ensure(self.base, "git", self.repo)
        code, text = run(self.base, here=os.path.join(self.repo, "src"))
        self.assertEqual(code, 0)
        first = text.splitlines()[0]
        self.assertTrue(first.startswith("here "), first)
        self.assertIn("(git)", first)
        self.assertIn("memory %s" % scope.short(scope.store_home(self.base, self.repo)), first)
        self.assertNotIn("above", text)

    def test_a_folder_that_is_gone_is_the_default_memory(self):
        code, text = run(self.base, here=os.path.join(self.tmp, "gone"))
        self.assertEqual(code, 0)
        self.assertIn("the default memory", text)

    def test_a_relative_path_is_read_from_the_current_folder(self):
        cwd = os.getcwd()
        self.addCleanup(os.chdir, cwd)
        os.chdir(self.repo)
        scope.ensure(self.base, "git", self.repo)
        _, text = run(self.base, here="src")
        self.assertTrue(text.startswith("here "), text)
        self.assertIn("(git)", text)

    def test_the_command_is_registered_with_the_breadcrumbs_cli(self):
        self.assertIn("scopes", [c["name"] for c in ports.commands()])


if __name__ == "__main__":
    unittest.main()
