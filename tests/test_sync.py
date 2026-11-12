"""`sync` for Claude Code: the sessions of a project folder land in the memory of that project, with a state.db and the
ports for the viewers. The fixture is a hand-written file with invented text. Run with breadcrumbs-common and this folder
on PYTHONPATH."""
import json
import os
import tempfile
import unittest
from unittest import mock

from breadcrumbs import ports, scope, statedb, sync

from breadcrumbs_claude import adapter

STAMP = "2026-01-02T03:04:05.000Z"


def turn(kind, content, cwd, **more):
    return json.dumps(dict({"type": kind, "cwd": cwd, "gitBranch": "dev", "timestamp": STAMP,
                            "message": {"role": kind, "content": content}}, **more))


class Sync(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = os.path.realpath(tmp.name)
        self.base = os.path.join(self.home, ".claude", "breadcrumbs")
        self.repo = os.path.join(self.home, "work", "kettle")
        os.makedirs(os.path.join(self.repo, ".git"))
        self.projects = os.path.join(self.home, ".claude", "projects")
        for name, cwd, text in (("kettle", self.repo, "how long to steep green tea?"),
                                ("stray", os.path.join(self.home, "nowhere"), "an invented question")):
            folder = os.path.join(self.projects, "-" + name)
            os.makedirs(folder)
            with open(os.path.join(folder, name + ".jsonl"), "w", encoding="utf-8") as f:
                f.write("\n".join([turn("user", text, cwd), turn("assistant", [{"type": "text", "text": "Two minutes."}], cwd,
                                    requestId="req_" + name)]) + "\n")

    def sync(self):
        return sync.sync("claude-code", self.projects, self.base, exclude=(), home=self.home)

    def test_a_session_goes_to_the_memory_of_the_repository_where_it_ran(self):
        out = self.sync()
        by = {s["scope"] or "default": s for s in out["stores"]}
        self.assertEqual((out["sessions"], out["new"]), (2, 2))
        self.assertEqual(by[scope.short(self.repo)]["sessions"], 1)
        self.assertEqual(by["default"]["sessions"], 1)  # its folder is gone and nothing above it is a project
        store = scope.store_home(self.base, self.repo)
        rows = statedb.read(statedb.locate(store), lambda c: c.execute(
            "SELECT id, git_repo_root, git_branch, created_source FROM sessions").fetchall())
        self.assertEqual(rows, [("kettle", self.repo, "dev", "claude-code")])

    def test_the_ports_place_a_folder_as_sync_does(self):
        self.assertEqual(ports.get("profile")("/anywhere"), adapter.NAME)
        self.assertIsNone(ports.get("codebase")(os.path.join(self.repo, "src")))  # the test repository is in a temporary folder
        with mock.patch.object(sync, "no_project", return_value=[]):
            self.assertEqual(ports.get("codebase")(os.path.join(self.repo, "src")), self.repo)
        self.assertIsNone(ports.get("codebase")(os.path.expanduser("~")))  # the home folder: the default memory
        self.assertIs(ports.get("state"), statedb.read)


if __name__ == "__main__":
    unittest.main()
