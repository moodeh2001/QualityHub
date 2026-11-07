"""Explicit test isolation; no reset/delete operations or secret exports."""
import os
from pathlib import Path
import tempfile
import pytest
import psycopg
from psycopg.rows import dict_row
from clients.api import ApiClient


def pytest_addoption(parser):
    parser.addoption('--allow-skips', action='store_true', help='Exploratory partial run; permits skipped tests')


def pytest_collection_modifyitems(items):
    for index, item in enumerate(items):
        item._qh_case_index = index


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    root = Path(os.getenv('QH_REPORT_ROOT', 'reports'))
    root.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix='pytest-', dir=root))
    config._qh_report_folder = folder
    config.option.xmlpath = str(folder / 'junit.xml')
    if hasattr(config.option, 'htmlpath'):
        config.option.htmlpath = str(folder / 'pytest.html')
        config.option.self_contained_html = True


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.skipped:
        item.config._qh_had_skip = True
        report.longrepr = (str(item.path), 0, 'Skipped: setup unavailable (details withheld)')
    report.nodeid = f'{item.path.name}::{getattr(item, "originalname", None) or item.name}[case-{getattr(item, "_qh_case_index", 0)}]'
    # Never persist assertion values, response bodies, captured logs or credentials.
    if report.failed:
        report.longrepr = f'{getattr(item, "originalname", None) or item.name}: {report.when} failed (sensitive details withheld)'
    report.sections = []
    report.user_properties = []
    report.extras = []


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config, '_qh_had_skip', False) and not session.config.getoption('--allow-skips') and exitstatus == 0:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
    import json
    folder = getattr(session.config, '_qh_report_folder', None)
    if folder:
        (folder / 'run.json').write_text(json.dumps({'status': 'PASS' if session.exitstatus == 0 else 'FAIL', 'exitCode': int(session.exitstatus), 'hadSkippedTests': bool(getattr(session.config, '_qh_had_skip', False)), 'partialRunAllowed': session.config.getoption('--allow-skips')}), encoding='utf-8')


@pytest.fixture(scope='session')
def public_api():
    client = ApiClient()
    yield client
    client.close()


@pytest.fixture(scope='session')
def private_api(public_api):
    if os.getenv('QH_ALLOW_WRITES') != '1':
        pytest.skip('BLOCKED: QH_ALLOW_WRITES=1 required')
    if public_api.base_url != 'http://localhost:4000':
        pytest.fail('Private writes restricted to localhost:4000')
    key = os.getenv('QH_SANDBOX_KEY')
    credentials = None
    if os.getenv('QH_CREATE_SANDBOX') == '1':
        if key:
            pytest.fail('Conflicting sandbox settings: remove existing key before requesting disposable isolation')
        bootstrap = ApiClient(writable=True)
        try:
            data = bootstrap.json('POST', '/api/v1/sandbox', status=201, json={'label': 'QualityHub disposable automation'})
            key, credentials = data['apiKey'], data['demoUser']
        finally:
            bootstrap.close()
    if not isinstance(key, str) or not key.strip():
        pytest.fail('Private sandbox setup returned no usable key')
    client = ApiClient(key=key, writable=True)
    state = client.request('GET', '/api/v1/sandbox/state')
    assert state.status_code == 200 and state.headers.get('X-Sandbox-Mode') == 'private', 'Private sandbox verification failed'
    client.sandbox_id = state.json()['sandboxId']
    client.credentials = credentials or {'email': os.getenv('QH_LOGIN_EMAIL'), 'password': os.getenv('QH_LOGIN_PASSWORD')}
    yield client
    client.close()


@pytest.fixture
def cart(private_api):
    return private_api.json('POST', '/api/v1/carts', status=201)['cart']


@pytest.fixture
def variant(private_api):
    for product in private_api.json('GET', '/api/v1/products?size=100')['items']:
        variants = private_api.json('GET', f"/api/v1/products/{product['id']}/variants")['variants']
        for item in variants:
            if item['available'] >= 5:
                return dict(item, product_id=product['id'])
    pytest.fail('No active fixture variant with five available units')


@pytest.fixture(scope='session')
def db():
    dsn = os.getenv('QH_DATABASE_DSN')
    if not dsn:
        pytest.skip('BLOCKED: QH_DATABASE_DSN required')
    try:
        connection = psycopg.connect(dsn, connect_timeout=5, autocommit=True,
            options='-c default_transaction_read_only=on', row_factory=dict_row)
    except psycopg.Error:
        pytest.fail('Database connection failed; check private QH_DATABASE_DSN (value redacted)')
    yield connection
    connection.close()
