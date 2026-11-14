"""The hierarchy skill of this plugin: skills/hierarchy/SKILL.md is generated from breadcrumbs/skills/hierarchy/hierarchy.md
(tools/skills.py in the umbrella repository), so it is not edited here. This plugin is the public one: no ACE, no D3M."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "hierarchy", "SKILL.md")
NOT_HERE = re.compile(r"\bACE\b|\bace_|\bace\.log|\bfold[ _]hook|\bbc-fold|\bD3M\b|\bclaude-api\b", re.I)


class HierarchySkillTest(unittest.TestCase):
    def setUp(self):
        with open(SKILL, encoding="utf-8") as f:
            self.text = f.read()

    def test_the_frontmatter_names_the_skill_and_its_description_fits(self):
        head = re.match(r"---\nname: hierarchy\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(head)
        assert head is not None
        self.assertTrue(0 < len(head.group(1)) <= 60, head.group(1))

    def test_it_teaches_each_lane_and_leaves_no_template_marker(self):
        for word in ("pinpoint", "scaffold", "dispatch", "fan-out", "inspect", "validate", "trim", "orchestrate"):
            self.assertIn(word, self.text)
        self.assertNotIn("<!--", self.text)
        self.assertNotIn("@@", self.text)

    def test_the_public_plugin_carries_no_ace_and_no_d3m(self):
        found = NOT_HERE.search(self.text)
        self.assertIsNone(found, found and found.group(0))

    def test_the_command_line_it_teaches_is_a_file_of_this_plugin(self):
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/bin/bc", self.text)
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "bin", "bc")))
        self.assertNotIn("${HERMES_SKILL_DIR}", self.text)


if __name__ == "__main__":
    unittest.main()
