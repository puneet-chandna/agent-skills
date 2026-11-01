"""Package/link checks and fail-closed tests for the public k6 summary CLI."""
import ast
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'optimize-server-performance'
CHECKER = SKILL / 'scripts' / 'check_k6_summary.py'


class PackageTests(unittest.TestCase):
    def test_skill_frontmatter_and_portable_layout(self):
        content = (SKILL / 'SKILL.md').read_text()
        front = content.split('---', 2)[1]
        self.assertRegex(front, r'(?m)^name: optimize-server-performance$')
        self.assertRegex(front, r'(?m)^description: .+')
        self.assertNotIn('/root/', content)
        self.assertNotIn('/workspace/', content)
        self.assertTrue((SKILL / 'references' / 'upstream-license.txt').is_file())
        self.assertTrue((ROOT / 'LICENSE').is_file())
        self.assertLess(len(content.splitlines()), 100)
        ast.parse(CHECKER.read_text())

    def test_relative_markdown_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith(('#', 'mailto:')):
                    continue
                file_part = unquote(target.split('#')[0])
                if file_part:
                    with self.subTest(document=str(path.relative_to(ROOT)), target=target):
                        self.assertTrue((path.parent / file_part).exists())

    def test_svg_assets_and_readme_image_resolve(self):
        for path in ROOT.rglob('*.svg'):
            with self.subTest(svg=path.name):
                self.assertEqual(ET.fromstring(path.read_text()).tag,
                                 '{http://www.w3.org/2000/svg}svg')
        self.assertTrue((ROOT / 'docs/assets/banner.svg').is_file())
        self.assertIn('docs/assets/banner.svg', (ROOT / 'README.md').read_text())
        metadata = (SKILL / 'agents/openai.yaml').read_text()
        for icon in re.findall(r'icon_(?:small|large):\s*[\"\']?([^\s\"\']+)', metadata):
            self.assertTrue((SKILL / icon).is_file())


class K6SummaryTests(unittest.TestCase):
    def run_summary(self, data, expected, options=(), raw=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'summary.json'
            path.write_text(data if raw else json.dumps(data))
            run = subprocess.run([sys.executable, str(CHECKER), str(path), *options],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
            return json.loads(run.stdout)

    @staticmethod
    def summary(p95=10, p99=20, errors=0, count=100):
        return {'metrics': {
            'http_req_duration': {'p(95)': p95, 'p(99)': p99},
            'http_req_failed': {'rate': errors},
            'http_reqs': {'count': count},
        }}

    def test_supported_summary_formats(self):
        original = self.summary()
        wrapped = {'metrics': {k: {'values': v} for k, v in original['metrics'].items()}}
        for data in (original, wrapped):
            with self.subTest(data=data):
                self.assertEqual(self.run_summary(data, 0)['status'], 'PASS')

    def test_thresholds_are_exclusive(self):
        for data in (self.summary(p95=500, p99=600), self.summary(p99=1000),
                     self.summary(errors=.01)):
            with self.subTest(data=data):
                self.assertEqual(self.run_summary(data, 1)['status'], 'FAIL')

    def test_missing_or_invalid_data_is_unverified(self):
        missing = self.summary()
        del missing['metrics']['http_req_duration']['p(99)']
        for data in (missing, [], self.summary(count=0), self.summary(count=True),
                     self.summary(errors=-.1), self.summary(p99=float('nan')),
                     self.summary(p95=30, p99=20)):
            with self.subTest(data=data):
                self.assertEqual(self.run_summary(data, 2)['status'], 'UNVERIFIED')
        self.run_summary('{broken', 2, raw=True)

    def test_custom_slos_are_enforced(self):
        self.run_summary(self.summary(p95=250, p99=400), 1,
                         ('--p95-ms', '200', '--p99-ms', '500'))
        self.run_summary(self.summary(), 2, ('--max-error-rate', 'nan'))

    def test_tagged_write_failures_are_visible_not_hidden(self):
        data = self.summary()
        data['metrics']['http_req_failed{name:POST /orders}'] = {'rate': .14}
        data['metrics']['checks'] = {'rate': .5}
        report = self.run_summary(data, 0)
        self.assertEqual(report['tagged_metrics']['http_req_failed{name:POST /orders}']['rate'], .14)
        self.assertEqual(report['check_success_rate'], .5)
        self.assertIn('not API correctness', report['scope'])
        self.assertTrue(report['limitations'])

    def test_missing_file_is_unverified(self):
        with tempfile.TemporaryDirectory() as folder:
            run = subprocess.run([sys.executable, str(CHECKER), str(Path(folder) / 'missing.json')],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(json.loads(run.stdout)['status'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
