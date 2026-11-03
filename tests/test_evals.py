"""Preparation and contamination checks only; no model execution."""
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'evals' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvaluationPackagingTests(unittest.TestCase):
    def test_conditions_isolation_and_no_candidate_leak(self):
        prepare = load('prepare')
        audit = load('audit').audit
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for condition in ('A', 'B', 'C'):
                out = root / condition
                manifest = prepare.prepare(out, condition, 'mode1', 'HEAD')
                task = out / 'task'
                files = set(subprocess.check_output(['git', '-C', str(task),
                    'ls-files'], text=True).splitlines())
                self.assertEqual(files, {'app.py', 'data.py', 'baseline.py', 'bench.py',
                                         'protocol.json', 'README.md', 'candidate.json'})
                self.assertEqual(subprocess.check_output(['git', '-C', str(task),
                    'rev-list', '--count', 'HEAD'], text=True).strip(), '1')
                self.assertEqual(subprocess.check_output(['git', '-C', str(task),
                    'status', '--porcelain'], text=True), '')
                self.assertEqual(subprocess.check_output(['git', '-C', str(task),
                    'remote'], text=True), '')
                self.assertEqual(manifest['candidate_entry_point']['manifest'], 'candidate.json')
                self.assertIsNone(json.loads((task / 'candidate.json').read_text())['implementation'])
                self.assertNotIn('tune', (out / 'task/bench.py').read_text())
                isolated = root / ('machine-' + condition)
                (isolated / 'inputs').mkdir(parents=True)
                if condition != 'A':
                    import shutil
                    shutil.copytree(out / 'control/guide', isolated / 'inputs/guide')
                self.assertEqual(audit(isolated, condition)['status'], 'PASS')
                (isolated / 'SKILL.md').write_text('name: optimize-server-performance')
                self.assertEqual(audit(isolated, condition)['status'], 'FAIL')
                if condition == 'B':
                    self.assertEqual(manifest['skill_revision'], prepare.BASELINE)
            out = root / 'missing'
            prepare.prepare(out, 'A', 'missing-measurement')
            self.assertFalse((out / 'task/bench.py').exists())
            self.assertNotIn('bench.py supports', (out / 'task/README.md').read_text())

    def test_grades_selected_candidate_including_setup_and_rejects_wrong_one(self):
        prepare = load('prepare')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'run'
            prepare.prepare(root, 'A', 'mode1')
            task, control = root / 'task', root / 'control'
            env = {**os.environ, 'EVAL_EXPORTED_TASK': str(task)}
            def grade(name):
                (task / 'candidate.json').write_text(json.dumps({'implementation': name}))
                return subprocess.run([sys.executable, str(control / 'test_contract.py'), '-v'],
                                      env=env, capture_output=True, text=True, timeout=30)
            # The untouched baseline remains correct throughout the selection tests.
            baseline = grade('baseline')
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            good = task / 'chosen.py'
            good.write_text('from baseline import render as original\n'
                            'ready = False\n'
                            'def prepare(path):\n    global ready\n    ready = True\n'
                            'def render(rows, selected):\n    assert ready\n'
                            '    return original(rows, selected)\n')
            result = grade('chosen')
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((control / 'graded-candidate.json').read_text())
            self.assertEqual(manifest['implementation'], 'chosen')
            self.assertEqual(manifest['sources']['chosen.py'], hashlib.sha256(good.read_bytes()).hexdigest())
            (task / 'wrong.py').write_text('def render(rows, selected):\n'
                                          '    return b\'{"items":[]}\', 12\n')
            result = grade('wrong')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('FAILED', result.stderr)
            self.assertEqual(json.loads((control / 'graded-candidate.json').read_text())['implementation'], 'wrong')
            self.assertEqual(grade('baseline').returncode, 0)
            self.assertNotEqual(grade(None).returncode, 0)
            self.assertFalse((control / 'graded-candidate.json').exists())


if __name__ == '__main__':
    unittest.main()
