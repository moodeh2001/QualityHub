"""HTTP client with local-only writes and secret-safe errors."""
import os
from decimal import Decimal, ROUND_HALF_UP
import requests
from urllib.parse import urlsplit


def money(value):
    return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class ApiClient:
    def __init__(self, base_url=None, key=None, writable=False):
        self.base_url = (base_url or os.getenv('QH_BASE_URL', 'http://localhost:4000')).rstrip('/')
        self.session = requests.Session()
        self.session.trust_env = False
        if key:
            self.session.headers['X-Sandbox-Key'] = key
        self.writable = writable

    def request(self, method, path, **kwargs):
        target = self.base_url + path
        if not path.startswith('/') or path.startswith('//') or urlsplit(target).netloc != urlsplit(self.base_url).netloc:
            raise RuntimeError('Invalid API destination')
        if kwargs.pop('allow_redirects', False):
            raise RuntimeError('Automatic redirects are forbidden')
        if method.upper() not in ('GET', 'HEAD'):
            if self.base_url != 'http://localhost:4000' or not self.writable:
                raise RuntimeError('Writes require authorized local test isolation')
        return self.session.request(method, target, timeout=15, allow_redirects=False, **kwargs)

    def json(self, method, path, status=200, **kwargs):
        response = self.request(method, path, **kwargs)
        assert response.status_code == status, f'{method} {path}: expected {status}, got {response.status_code}'
        assert 'application/json' in response.headers.get('Content-Type', ''), 'Expected JSON content type'
        data = response.json()
        assert isinstance(data, dict), 'Expected JSON object'
        return data

    def close(self):
        self.session.close()


def assert_cart(data):
    items, totals = data['items'], data['totals']
    subtotal = money(sum((money(i['unit_price']) * i['qty'] for i in items), Decimal(0)))
    for item in items:
        assert money(item['line_total']) == money(money(item['unit_price']) * item['qty'])
    assert money(totals['subtotal']) == subtotal
    assert data['itemCount'] == sum(i['qty'] for i in items)
    assert money(totals['shipping_total']) == (Decimal('0.00') if subtotal >= 500 else Decimal('29.90'))
    assert money(totals['grand_total']) == money(subtotal - money(totals['discount_total']) + money(totals['shipping_total']))
