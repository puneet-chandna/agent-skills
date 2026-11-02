"""Document regression checks, not agent behavioral evaluations."""
import re
import unittest

from test_package import ROOT, SKILL


class InstructionTests(unittest.TestCase):
    def test_editorial_budget_and_description(self):
        text = (SKILL / 'SKILL.md').read_text()
        front, body = text.split('---', 2)[1:]
        description = re.search(r'^description: (.+)$', front, re.M)[1]
        self.assertLess(len(description), 700)
        self.assertIn('$12 Server Challenge', description)
        # Explicit upper budget; no minimum and no claim that length measures quality.
        self.assertLessEqual(len(body.split()), 500)

    def test_readme_install_arguments_name_real_skills(self):
        readme = (ROOT / 'README.md').read_text()
        names = re.findall(r'--skill\s+([\w-]+)', readme)
        self.assertTrue(names)
        for name in names:
            self.assertTrue((ROOT / 'skills' / name / 'SKILL.md').is_file(), name)

    def test_required_sections_and_reading(self):
        text = (SKILL / 'SKILL.md').read_text()
        self.assertEqual(len(re.findall(r'^## [1-5]\. ', text, re.M)), 5)
        self.assertIn('## Deliver', text)
        for phrase in ('Selecting a mode', 'selected mode', 'inherited',
                       'Validation ladder', 'measurement.md', 'technique-catalog.md'):
            self.assertIn(phrase, text)
        for mode in ('**1', '**2', '**3'):
            self.assertIn(mode, text)

    def test_document_invariants(self):
        text = (SKILL / 'SKILL.md').read_text()
        for phrase in ('Default to Mode 1', 'including subtasks', 'ceiling',
                       'Narrower user constraints prevail', 'compatibility',
                       'operational responsibilities', 'destructive migrations',
                       'live deployment', 'machine-wide changes',
                       'before candidate measurements', 'three interleaved',
                       'five in Mode 3', 'changed layer', 'sustained', 'fault',
                       'Never average percentiles', 'cherry-pick', 'rare-route',
                       'UNVERIFIED', 'universal success', 'another implementation',
                       'project journal', 'installed skill'):
            with self.subTest(invariant=phrase):
                self.assertIn(phrase, text)


if __name__ == '__main__':
    unittest.main()
