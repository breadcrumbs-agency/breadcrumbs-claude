"""The dispatch skill and the lane agents of this plugin: skills/dispatch/SKILL.md and agents/<lane>.md are generated from
breadcrumbs/skills/dispatch (tools/skills.py in the umbrella repository), so they are not edited here. This plugin is
the public one: no ACE, no D3M."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "dispatch", "SKILL.md")
LANES = ("lead", "build", "cheap", "check")
NOT_HERE = re.compile(r"\bACE\b|\bace_|\bace\.log|\bfold[ _]hook|\bbc-fold|\bD3M\b|\bclaude-api\b", re.I)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def front(text):
    head = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert head is not None
    return dict(line.split(": ", 1) for line in head.group(1).splitlines())


class DispatchSkillTest(unittest.TestCase):
    def setUp(self):
        self.text = read(SKILL)

    def test_the_frontmatter_names_the_skill_and_its_description_fits(self):
        head = front(self.text)
        self.assertEqual(head["name"], "dispatch")
        self.assertTrue(0 < len(head["description"]) <= 60, head["description"])

    def test_it_teaches_each_lane_and_leaves_no_template_marker(self):
        for word in ("pinpoint", "scaffold", "dispatch", "fan-out", "inspect", "validate", "trim", "orchestrate"):
            self.assertIn(word, self.text)
        self.assertNotIn("<!--", self.text)
        self.assertNotIn("@@", self.text)

    def test_the_public_plugin_carries_no_ace_and_no_d3m(self):
        for path in [SKILL] + [os.path.join(ROOT, "agents", lane + ".md") for lane in LANES]:
            found = NOT_HERE.search(read(path))
            self.assertIsNone(found, (path, found and found.group(0)))

    def test_the_command_line_it_teaches_is_a_file_of_this_plugin(self):
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/bin/bc", self.text)
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "bin", "bc")))
        self.assertNotIn("${HERMES_SKILL_DIR}", self.text)


class LaneAgentTest(unittest.TestCase):
    def test_each_lane_is_an_agent_with_the_model_and_effort_of_its_row(self):
        rows = {r[0].split()[0]: r for r in ([c.strip() for c in line.strip("|").split("|")]
                                             for line in read(SKILL).splitlines() if line.startswith("| "))}
        for lane in LANES:
            head = front(read(os.path.join(ROOT, "agents", lane + ".md")))
            self.assertEqual(head["name"], lane)
            self.assertEqual(head["model"], rows[lane][2])
            self.assertEqual(head["effort"], rows[lane][3])
            self.assertIn(head["effort"], ("low", "medium", "high", "xhigh", "max"))


if __name__ == "__main__":
    unittest.main()
