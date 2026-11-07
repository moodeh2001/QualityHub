"""Regression checks use fake responses/credentials, never the QA database."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import pytest
import requests
from requests.adapters import BaseAdapter
from clients.api import ApiClient

ROOT = Path(__file__).resolve().parents[2]


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RedirectAdapter(BaseAdapter):
    def __init__(self):
        self.targets = []

    def send(self, request, **kwargs):
        self.targets.append(request.url)
        response = requests.Response()
        response.status_code = 307
        response.headers['Location'] = 'http://127.0.0.1:45678/collect'
        response._content = b''
        response.request = request
        response.url = request.url
        return response

    def close(self):
        pass


def test_redirect_does_not_forward_credentials():
    client = ApiClient(key='fake-sandbox', writable=True)
    adapter = RedirectAdapter()
    client.session.mount('http://', adapter)
    try:
        response = client.request('POST', '/api/v1/carts', json={'password': 'fake-password'})
        assert response.status_code == 307
        assert adapter.targets == ['http://localhost:4000/api/v1/carts']
        with pytest.raises(RuntimeError):
            client.request('POST', '/api/v1/carts', allow_redirects=True)
    finally:
        client.close()


def test_disposable_conflict_rejected_before_network(monkeypatch):
    fixtures = load('tests/conftest.py', 'fixture_policy')
    monkeypatch.setenv('QH_ALLOW_WRITES', '1')
    monkeypatch.setenv('QH_CREATE_SANDBOX', '1')
    monkeypatch.setenv('QH_SANDBOX_KEY', 'fake-existing-key')
    with pytest.raises(pytest.fail.Exception, match='Conflicting sandbox'):
        next(fixtures.private_api.__wrapped__(ApiClient()))


def test_empty_created_key_fails_setup(monkeypatch):
    fixtures = load('tests/conftest.py', 'empty_key_policy')
    monkeypatch.setenv('QH_ALLOW_WRITES', '1')
    monkeypatch.setenv('QH_CREATE_SANDBOX', '1')
    monkeypatch.delenv('QH_SANDBOX_KEY', raising=False)
    class Bootstrap:
        def __init__(self, **kwargs): pass
        def json(self, *args, **kwargs):
            return {'apiKey': '', 'demoUser': {'email': 'fake', 'password': 'fake'}}
        def close(self): pass
    monkeypatch.setattr(fixtures, 'ApiClient', Bootstrap)
    with pytest.raises(pytest.fail.Exception, match='no usable key'):
        next(fixtures.private_api.__wrapped__(ApiClient()))


def test_required_skip_exit_and_report_redaction():
    report_root = Path(os.environ.get('QH_REPORT_ROOT', ROOT/'reports')).resolve()
    report_root.mkdir(parents=True, exist_ok=True)
    tmp_path = Path(tempfile.mkdtemp(prefix='regression-', dir=report_root))
    (tmp_path/'conftest.py').write_text((ROOT/'tests/conftest.py').read_text())
    (tmp_path/'test_child.py').write_text('import pytest\ndef test_skip(): pytest.skip("blocked")\ndef test_secret():\n print("fake-token-do-not-persist")\n pytest.fail("fake-token-do-not-persist")\n')
    env = dict(os.environ, QH_REPORT_ROOT=str(tmp_path/'reports'), PYTHONPATH=str(ROOT))
    command = [sys.executable, '-m', 'pytest', str(tmp_path), '-c', str(ROOT/'pytest.ini'), '-p', 'no:cacheprovider', '-q']
    failed = subprocess.run(command, env=env, capture_output=True, text=True)
    assert failed.returncode == 1
    assert 'fake-token-do-not-persist' not in failed.stdout + failed.stderr
    files = list((tmp_path/'reports').rglob('junit.xml'))
    assert len(files) == 1 and 'fake-token-do-not-persist' not in files[0].read_text()
    assert all('fake-token-do-not-persist' not in p.read_text(encoding='utf-8') for p in (tmp_path/'reports').rglob('*.html'))
    skipped = subprocess.run(command + ['-k', 'test_skip'], env=env, capture_output=True, text=True)
    assert skipped.returncode == 1, 'Required skipped tests must fail the run'
    assert len(list((tmp_path/'reports').rglob('junit.xml'))) == 2


def test_pagination_rejects_empty_page():
    tests = load('tests/api/test_api.py', 'page_contract')
    class Empty:
        def json(self, *args): return {'page':1, 'size':2, 'total':100, 'items':[]}
    with pytest.raises(AssertionError): tests.test_pagination(Empty(), 1, 2)


def test_pagination_rejects_duplicate_pages():
    tests = load('tests/api/test_api.py', 'distinct_page_contract')
    class Duplicate:
        def json(self, *args): return {'total':100, 'items':[{'id':1},{'id':2}]}
    with pytest.raises(AssertionError): tests.test_pages_are_distinct(Duplicate())


def test_sandbox_check_rejects_absent_cart():
    tests = load('tests/integration/test_cart_database.py', 'cart_presence_contract')
    class Empty:
        def execute(self, *args): return self
        def fetchall(self): return []
    with pytest.raises(AssertionError):
        tests.test_database_sandbox_boundary(Empty(), type('Private', (), {'sandbox_id':'fake'})(), {'id':123})
