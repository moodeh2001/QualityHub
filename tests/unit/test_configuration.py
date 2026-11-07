"""Validate Python CI and local exposure policies."""
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]




def test_ports_are_loopback_bound():
    compose=yaml.safe_load((ROOT/'compose.yaml').read_text(encoding='utf-8'))
    assert compose['services']['api']['ports']==['127.0.0.1:4000:4000']
    assert compose['services']['db']['ports']==['127.0.0.1:5433:5432']


def test_fork_regressions_do_not_require_secrets():
    workflow=yaml.safe_load((ROOT/'.github/workflows/backend-qa.yml').read_text())
    regression=workflow['jobs']['regression']
    assert 'if' not in regression
    assert '${{ secrets.' not in str(regression)
    assert 'tests/unit' in str(regression)
    assert 'setup-node' not in str(workflow) and 'npm ' not in str(workflow)
    assert 'head.repo.full_name == github.repository' in workflow['jobs']['backend']['if']
    assert workflow['jobs']['backend']['env']['QH_REPORT_ROOT'].startswith('reports/ci-')
