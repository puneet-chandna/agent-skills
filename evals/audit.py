"""Fail-closed filesystem preflight; run in the disposable evaluation machine."""
import argparse
import json
import os
from pathlib import Path


def audit(root, condition):
    findings, errors, copies = [], [], []
    root = Path(root).resolve()
    allowed = root / 'inputs' / 'guide'
    skipped = {root / name for name in ('proc', 'sys', 'dev')}
    def onerror(error):
        errors.append(str(error))
    for folder, dirs, files in os.walk(root, onerror=onerror):
        parent = Path(folder)
        # Symlink targets must be within the audited tree, outside virtual FS.
        for name in list(dirs):
            path = parent / name
            if path in skipped:
                dirs.remove(name)
            elif path.is_symlink():
                target = path.resolve()
                if not target.is_relative_to(root) or any(target.is_relative_to(p) for p in skipped):
                    errors.append(f'unauditable symlink: {path}')
        for name in files:
            path = parent / name
            if name != 'SKILL.md':
                continue
            try:
                if path.is_symlink():
                    errors.append(f'symlinked skill: {path}')
                content = path.read_text()
            except (OSError, UnicodeError) as error:
                errors.append(str(error))
                continue
            if 'name: optimize-server-performance' in content:
                copies.append(str(path))
                if condition == 'A' or not path.is_relative_to(allowed):
                    findings.append(str(path))
    expected = 0 if condition == 'A' else 1
    if len(copies) != expected:
        errors.append(f'expected {expected} target copies, found {len(copies)}')
    return dict(condition=condition, root=str(root), target_copies=copies,
                forbidden_copies=findings, errors=errors,
                skipped_virtual_filesystems=[str(p) for p in sorted(skipped)],
                status='PASS' if not findings and not errors else 'FAIL',
                limitation='Also inspect mounts, CLI context, bundled resources and plugins; scan is not isolation.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--condition', choices='ABC', required=True)
    args = parser.parse_args()
    result = audit(args.root, args.condition)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
