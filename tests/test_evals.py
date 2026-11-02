"""Preparation and contamination checks only; no model execution."""
import importlib.util
from pathlib import Path
import tempfile
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
                manifest = prepare.prepare(out, condition, 'mode1', prepare.BASELINE)
                files = {p.name for p in (out / 'task').rglob('*') if p.is_file()}
                self.assertEqual(files, {'app.py', 'data.py', 'baseline.py', 'bench.py',
                                         'protocol.json', 'README.md'})
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


if __name__ == '__main__':
    unittest.main()
