"""Run Python regressions in source-only snapshots, without historical reports.

Uses the invoking interpreter's installed dependencies; this is not a clean
dependency installation. Private environment values are excluded from child runs.
Snapshots/evidence stay under the ignored .verification directory.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRS = ('.github', 'clients', 'tests', 'sql', 'postman', 'docs', 'tools')
SOURCE_FILES = ('AGENTS.md', 'README.md', '.gitignore', '.env.example',
                'requirements.txt', 'pytest.ini', 'compose.yaml')


def main():
    run = ROOT / '.verification' / ('clean-' + uuid.uuid4().hex)
    run.mkdir(parents=True)
    results = []
    for name in ('default', 'custom'):
        source = run / name
        source.mkdir()
        for directory in SOURCE_DIRS:
            shutil.copytree(ROOT / directory, source / directory,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for filename in SOURCE_FILES:
            shutil.copy2(ROOT / filename, source / filename)
        assert not (source / 'reports').exists()
        env = {key: value for key, value in os.environ.items()
               if not key.startswith('QH_') and key not in ('PYTHONPATH', 'PYTEST_ADDOPTS', 'PYTEST_PLUGINS')}
        env['QH_ALLOW_WRITES'] = '0'
        report_root = source / 'reports' if name == 'default' else run / 'custom-evidence'
        if name == 'custom':
            env['QH_REPORT_ROOT'] = str(report_root)
        completed = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/unit', '-p', 'no:cacheprovider', '-q'],
            cwd=source, env=env, capture_output=True, text=True)
        print(completed.stdout, end='')
        if completed.stderr:
            print(completed.stderr, end='', file=sys.stderr)
        if name == 'custom':
            assert not (source / 'reports').exists(), 'Custom report run wrote project-local reports'
        manifests = sorted(report_root.glob('pytest-*/run.json'))
        assert len(manifests) == 1, 'Expected exactly one outer run manifest'
        status = json.loads(manifests[0].read_text())
        results.append({'mode': name, 'source': str(source), 'report': str(manifests[0].parent),
                        'exitCode': completed.returncode, 'manifest': status,
                        'startedWithoutReports': True,
                        'customSourceHasNoReports': name == 'custom' and not (source / 'reports').exists()})
    (run / 'verification.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    print('Clean-source evidence: ' + str(run / 'verification.json'))
    return 0 if all(r['exitCode'] == 0 and r['manifest']['status'] == 'PASS' for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
