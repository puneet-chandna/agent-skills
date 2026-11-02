"""Document regression checks, not agent behavioral evaluations."""
import re
import hashlib
import json
import unittest

from test_package import ROOT, SKILL


class InstructionTests(unittest.TestCase):
    def test_protected_and_historical_files_unchanged(self):
        expected_hashes = {
            'upstream-license.txt': '1c809f52dd742570746a8ac00694ad4ddd9229e12accc7d5c598075861b478a0',
            'submission-catalog.json': '0d320d4e9b3844f38403e2e092985411b2024e4b09b447f56f2aaab0cfbbbd10',
            'case-studies.md': 'a2f13cd3fe5c7ee31a0d75c6e663e8b5b6495f953738834d714780927e4579a5',
            'technique-catalog.md': 'cc05b5ff02908b01c84a71f72e6f96fa7f46f57f017b89a176ec6d2a87ab83c6',
            'optimization-playbook.md': 'e92bcd2f349e16c3b9cd17cd38f3588c4a70ba5ccaa44eecfe957df9fd8bdf5d',
        }
        for name, expected in expected_hashes.items():
            path = SKILL / 'references' / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_agent_results_remain_blank(self):
        results = json.loads((ROOT / 'evals/results-template.json').read_text())
        self.assertEqual(results['status'], 'NOT RUN')
        self.assertEqual(results['trials'], [])

    def test_editorial_budget_and_description(self):
        text = (SKILL / 'SKILL.md').read_text()
        front, body = text.split('---', 2)[1:]
        description = re.search(r'^description: (.+)$', front, re.M)[1]
        self.assertLess(len(description), 700)
        self.assertIn('$12 Server Challenge', description)
        # Expand shorthand and state inheritance explicitly. Editorial ceiling, no minimum.
        self.assertLessEqual(len(body.split()), 575)

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
        text = (SKILL / 'SKILL.md').read_text().split('---', 2)[2].lower()
        for phrase in ('default to mode 1', 'including subtasks', 'ceiling',
                       'Narrower user constraints prevail', 'compatibility',
                       'operational responsibilities', 'destructive migrations',
                       'live deployment', 'machine-wide changes',
                       'before candidate measurements', 'three interleaved',
                       'at least five pairs', 'changed layer', 'sustained', 'fault',
                       'does not inherit lower-mode architectural restrictions',
                       'Never average percentiles', 'cherry-pick', 'rare-route',
                       'UNVERIFIED', 'universal success', 'another implementation',
                       'project journal', 'installed skill'):
            with self.subTest(invariant=phrase):
                self.assertIn(phrase.lower(), text)


if __name__ == '__main__':
    unittest.main()
