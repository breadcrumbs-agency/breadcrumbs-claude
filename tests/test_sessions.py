"""The sessions of Claude Code as a source of the ingest. The fixture is a hand-written file with invented text.
Run with breadcrumbs-common and this folder on PYTHONPATH."""
import datetime
import json
import os
import unittest

from breadcrumbs import harness_case

STAMP = datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)
HERE = {"cwd": "/work/demo", "gitBranch": "main", "timestamp": "2026-01-02T03:04:05.000Z"}


def line(kind, content, **more):
    return json.dumps(dict({"type": kind, "message": {"role": kind, "content": content}}, **HERE, **more))


class Sessions(harness_case.SourceCase):
    KEY = "claude-code"

    def fixture(self, folder):
        project = os.path.join(folder, "projects", "-work-demo")
        os.makedirs(project)
        with open(os.path.join(project, "s1.jsonl"), "w", encoding="utf-8") as f:
            f.write("\n".join([
                json.dumps({"type": "ai-title", "aiTitle": "Boil an egg", "sessionId": "s1"}),
                line("user", "a caveat that Claude Code wrote", isMeta=True),
                line("user", "how long to boil an egg?"),
                line("assistant", [{"type": "thinking", "thinking": "hmm", "signature": "x"}]),
                line("assistant", [{"type": "text", "text": "Let me look at the clock."}]),
                line("assistant", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "date"}}]),
                line("user", [{"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "Fri 03:04"}]}]),
                json.dumps({"type": "attachment", "attachment": {"type": "hook_success"}}),
                "{this line is broken",
                line("assistant", [{"type": "text", "text": "About ten minutes."}]),
            ]) + "\n")
        return os.path.join(folder, "projects")

    def test_a_fixture_becomes_turns_and_tool_rows(self):
        (sid, _title, _meta, rows), = self.sessions()
        self.assertEqual(sid, "s1")
        self.assertEqual([(r["role"], r["content"]) for r in rows], [
            ("user", "how long to boil an egg?"), ("assistant", "Let me look at the clock."),
            ("tool", "Fri 03:04"), ("assistant", "About ten minutes.")])
        self.assertEqual(rows[1]["tool_calls"], [{"id": "t1", "function": {"name": "Bash", "arguments": {"command": "date"}}}])
        self.assertEqual((rows[2]["tool_name"], rows[2]["tool_call_id"]), ("Bash", "t1"))
        self.assertEqual({r["ts"] for r in rows}, {int(STAMP.timestamp())})

    def test_the_session_keeps_its_title_folder_and_branch(self):
        (_sid, title, meta, _rows), = self.sessions()
        self.assertEqual((title, meta["cwd"], meta["branch"]), ("Boil an egg", "/work/demo", "main"))

    def test_a_broken_line_is_skipped_and_counted(self):
        (_sid, _title, meta, rows), = self.sessions()
        self.assertEqual((meta["skipped"], len(rows)), ("1", 4))


if __name__ == "__main__":
    unittest.main()
