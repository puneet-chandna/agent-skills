"""Stage inputs only. Never invokes a model or copies a candidate/result/journal."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '9c854e1b0f43403aa09035140d6554cb4408b0f3'
CONTRACT = '''# Local feed fixture

Educational Python standard-library HTTP/SQLite application. Keep dependencies
within the standard library. The baseline is in baseline.py. app.py serves
loopback only. Generate a disposable database with data.seed(path, rows, 17).
GET /feed returns the first 1000 items ordered by score descending, then id
ascending. ?limit=N accepts one ASCII decimal integer 0..10000. Every item has
id, score, title, selected. Duplicate selected rows do not duplicate output;
titles can repeat and Unicode must survive. Reads see committed external changes.
The two table reads must share a transaction snapshot. Invalid query -> 400
{"error":"invalid limit"}; unknown route -> 404 {"error":"not found"}; POST ->
405 {"error":"method not allowed"}; DB failure -> 503 {"error":"database unavailable"}.
Content-Type is application/json; charset=utf-8; Content-Length is UTF-8 bytes.
Preserve the complete success JSON shape and compact UTF-8 encoding. This API
has no write endpoint, authentication or TLS responsibility. Do not add fake
sleeps, stale response caches, weaken checks or access live services/data.

Create your own useful correctness checks. bench.py supports matched local
experiments; start by comparing baseline against itself. No precomputed results
are supplied. Keep artifacts in this task. Report limitations and uncertainty.

Before completion, write candidate.json with {"implementation":"MODULE_NAME"}.
Select a Python module in this directory, including baseline if you retain it.
The hidden grader imports that module and starts app.make_server(database,
implementation=MODULE_NAME), including its setup. Preserve this test entry point
when rebuilding internals. A missing or null selection fails grading. Statements
in the final message do not override this output manifest.
'''


def prepare(out, condition, scenario, revision=None, rows=None):
    out = Path(out).resolve()
    if out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Use a new directory outside this repository')
    prompts = json.loads((ROOT / 'evals/prompts.json').read_text())
    task, control = out / 'task', out / 'control'
    task.mkdir(parents=True)
    control.mkdir()
    fixture = ROOT / 'examples/slow-api'
    files = ['data.py', 'app.py', 'baseline.py']
    if scenario != 'missing-measurement':
        files += ['bench.py', 'protocol.json']
    for name in files:
        shutil.copyfile(fixture / name, task / name)
    if (task / 'bench.py').exists():
        text = (task / 'bench.py').read_text()
        text = text.replace("parser.add_argument('--candidate', default='tune')",
                            "parser.add_argument('--candidate', default='baseline')")
        (task / 'bench.py').write_text(text)
    count = rows if rows is not None else (100000 if scenario == 'mode3' else 12000)
    contract = CONTRACT
    if scenario == 'missing-measurement':
        contract = contract.replace('bench.py supports matched local\nexperiments; start by comparing baseline against itself.',
                                    'Trustworthy performance measurement is unavailable for this task.')
    (task / 'README.md').write_text(contract + f'\nUse rows={count}, seed=17 for the target dataset.\n')
    (task / 'candidate.json').write_text('{"implementation":null}\n')
    git_env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    git_env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
    subprocess.run(['git', 'init', '--quiet', '--initial-branch=main', '--template=', str(task)],
                   env=git_env, check=True)
    subprocess.run(['git', '-C', str(task), 'add', '--', '.'], env=git_env, check=True)
    subprocess.run(['git', '-C', str(task), '-c', 'user.name=Fixture setup',
                    '-c', 'user.email=fixture@localhost', '-c', 'core.hooksPath=/dev/null',
                    'commit', '--quiet', '-m', 'Initial sanitized fixture'], env=git_env, check=True)
    guide_revision = BASELINE if condition == 'B' else revision
    if condition != 'A':
        if not guide_revision:
            raise ValueError('Condition C requires an immutable --revision')
        guide_revision = subprocess.check_output(['git', 'rev-parse', '--verify', guide_revision + '^{commit}'],
                                                 cwd=ROOT, text=True).strip()
        prefix = 'skills/optimize-server-performance/'
        names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', guide_revision,
                                         '--', prefix], cwd=ROOT, text=True).splitlines()
        for name in names:
            dest = control / 'guide' / name.removeprefix(prefix)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(subprocess.check_output(['git', 'show', guide_revision + ':' + name], cwd=ROOT))
    prompt = 'Work on the application in /workspace/task. Read README.md.\n' + prompts[scenario] + '\n'
    if condition != 'A':
        prompt += 'Apply the skill at /inputs/guide/SKILL.md and its required references.\n'
    (control / 'prompt.txt').write_text(prompt)
    shutil.copyfile(ROOT / 'evals/audit.py', control / 'audit.py')
    # This hidden oracle is kept on the evaluator host, never in the agent mount.
    shutil.copyfile(ROOT / 'tests/test_slow_api.py', control / 'test_contract.py')
    shutil.copyfile(fixture / 'data.py', control / 'trusted_data.py')
    manifest = dict(condition=condition, scenario=scenario, rows=count, seed=17,
                    skill_revision=guide_revision if condition != 'A' else None,
                    candidate_entry_point={'manifest': 'candidate.json', 'key': 'implementation',
                                           'factory': 'app.make_server(database, implementation)'},
                    fixture_commit=subprocess.check_output(['git', '-C', str(task),
                        'rev-parse', 'HEAD'], text=True).strip(),
                    files={str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(out.rglob('*')) if p.is_file()
                           and '.git' not in p.relative_to(out).parts})
    (control / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--condition', choices='ABC', required=True)
    parser.add_argument('--scenario', choices=json.loads((ROOT / 'evals/prompts.json').read_text()), required=True)
    parser.add_argument('--revision')
    parser.add_argument('--rows', type=int)
    args = parser.parse_args()
    print(json.dumps(prepare(args.out, args.condition, args.scenario, args.revision, args.rows), indent=2))
