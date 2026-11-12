"""The sessions of Claude Code as a source of the ingest. The fixture is a hand-written file with invented text.
Run with breadcrumbs-common and this folder on PYTHONPATH."""
import datetime
import json
import os
import tempfile
import unittest

from breadcrumbs import harness_case, ports

from breadcrumbs_claude import sessions

STAMP = datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)
HERE = {"cwd": "/work/demo", "gitBranch": "main", "timestamp": "2026-01-02T03:04:05.000Z"}


def line(kind, content, message=None, **more):
    return json.dumps(dict({"type": kind, "message": dict({"role": kind, "content": content}, **(message or {}))}, **HERE,
                           **more))


def use(inp, cr, cw, out):  # made-up counts of the Anthropic API
    return {"input_tokens": inp, "cache_read_input_tokens": cr, "cache_creation_input_tokens": cw, "output_tokens": out}


R1 = {"id": "msg_1", "model": "claude-demo", "usage": use(3, 0, 900, 40)}  # one response, written as three records
R2 = {"id": "msg_2", "model": "claude-demo", "usage": use(5, 900, 60, 12)}


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
                line("assistant", [{"type": "thinking", "thinking": "hmm", "signature": "x"}], R1, requestId="req_1"),
                line("assistant", [{"type": "text", "text": "Let me look at the clock."}], R1, requestId="req_1"),
                line("assistant", [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "date"}}], R1,
                     requestId="req_1"),
                line("user", [{"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "Fri 03:04"}]}]),
                json.dumps({"type": "attachment", "attachment": {"type": "hook_success"}}),
                "{this line is broken",
                line("assistant", [{"type": "text", "text": "About ten minutes."}], R2, requestId="req_2"),
                line("assistant", [], {"id": "msg_3", "model": "<synthetic>", "usage": use(0, 0, 0, 0)}, requestId="req_3"),
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

    def test_a_response_split_in_records_is_one_request(self):
        got = list(ports.harnesses()[self.KEY]["usage"](self.path))
        self.assertEqual([(r["req"], r["sess"], r["model"], r["prov"], r["src"]) for r in got],
                         [("req_1", "s1", "claude-demo", "anthropic", "claude-code"),
                          ("req_2", "s1", "claude-demo", "anthropic", "claude-code")], "once each; no synthetic record")
        self.assertEqual([(r["in"], r["cr"], r["cw"], r["out"], r["prompt"]) for r in got],
                         [(3, 0, 900, 40, 903), (5, 900, 60, 12, 965)], "Anthropic's input does not hold the cache")
        self.assertEqual({r["ts"] for r in got}, {int(STAMP.timestamp())})


class ResultsWithoutText(unittest.TestCase):
    """A tool result whose parts are not text keeps its result row: it is named, not dropped."""

    def rows(self, *results):
        calls = [{"type": "tool_use", "id": "t%d" % i, "name": name, "input": {}} for i, (name, _) in enumerate(results)]
        back = [{"type": "tool_result", "tool_use_id": "t%d" % i, "content": content} for i, (_, content) in enumerate(results)]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "s1.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                f.write(line("assistant", calls, {"id": "m", "model": "claude-demo", "usage": use(1, 0, 0, 1)}, requestId="r") + "\n")
                f.write(line("user", back) + "\n")
            return sessions.session(path)[3]

    def test_a_tool_reference_is_named_by_its_tool(self):
        (_call, result), = [self.rows(("ToolSearch", [{"type": "tool_reference", "tool_name": "WebFetch"}]))]
        self.assertEqual((result["tool_name"], result["content"]), ("ToolSearch", "WebFetch"))

    def test_an_image_is_named_by_its_media_type_and_text_beside_it_stays(self):
        rows = self.rows(("Shot", [{"type": "image", "source": {"type": "base64", "data": "AAAA", "media_type": "image/jpeg"}}]),
                         ("Both", [{"type": "text", "text": "seen"}, {"type": "image", "source": {}}]))
        self.assertEqual([r["content"] for r in rows if r["role"] == "tool"], ["[image/jpeg]", "seen\n[image]"])

    def test_an_unknown_part_adds_nothing(self):
        rows = self.rows(("Odd", [{"type": "audio", "data": "x"}]))
        self.assertEqual([r["role"] for r in rows], ["assistant"])


if __name__ == "__main__":
    unittest.main()
