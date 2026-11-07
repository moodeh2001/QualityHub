"""Contract-backed API checks; contract is served at /api/v1/openapi.yaml."""
import pytest
from clients.api import ApiClient, assert_cart, money

pytestmark = pytest.mark.api


def test_health(public_api):
    data = public_api.json('GET', '/health')
    assert data['status'] == 'ok' and data['database'] == 'up'


@pytest.mark.parametrize('page_number,size', [(1, 1), (1, 2), (2, 2), (1, 100)])
def test_pagination(public_api, page_number, size):
    data = public_api.json('GET', f'/api/v1/products?page={page_number}&size={size}')
    assert (data['page'], data['size']) == (page_number, size)
    assert len(data['items']) <= size and data['total'] >= len(data['items'])
    expected = max(0, min(size, data['total'] - (page_number - 1) * size))
    assert len(data['items']) == expected, 'Page cardinality contradicts total'
    assert len({i['id'] for i in data['items']}) == len(data['items'])
    assert all(i['is_active'] and money(i['price']) >= 0 for i in data['items'])


def test_pages_are_distinct(public_api):
    first = public_api.json('GET', '/api/v1/products?page=1&size=2')
    second = public_api.json('GET', '/api/v1/products?page=2&size=2')
    assert first['total'] == second['total']
    assert len(first['items']) == min(2, first['total'])
    assert len(second['items']) == max(0, min(2, first['total'] - 2))
    assert not ({p['id'] for p in first['items']} & {p['id'] for p in second['items']}), 'Pages overlap'


def test_product_and_variants(public_api):
    product = public_api.json('GET', '/api/v1/products?size=1')['items'][0]
    assert public_api.json('GET', f"/api/v1/products/{product['id']}")['product']['id'] == product['id']
    data = public_api.json('GET', f"/api/v1/products/{product['id']}/variants")
    assert data['productId'] == product['id'] and data['total'] == len(data['variants'])
    assert data['variants']
    for v in data['variants']:
        assert v['id'] > 0 and v['sku']
        assert v['available'] == v['stock_qty'] - v['reserved_qty']


@pytest.mark.parametrize('path,status', [('/api/v1/products/999999999',404),('/api/v1/products/abc',400),('/api/v1/products?sort=invalid',400)])
def test_product_errors(public_api, path, status):
    assert public_api.json('GET', path, status=status)['error']['code']


@pytest.mark.parametrize('header', [None, 'Bearer invalid-token'])
def test_missing_invalid_token(public_api, header):
    headers = {'Authorization': header} if header else {}
    assert public_api.json('GET', '/api/v1/auth/me', status=401, headers=headers)['error']['code'] == 'UNAUTHORIZED'


def test_invalid_sandbox(public_api):
    assert public_api.json('GET','/api/v1/products',status=401,headers={'X-Sandbox-Key':'invalid-qualityhub-key'})['error']['code'] == 'UNAUTHORIZED'


def test_public_readonly_mode(public_api):
    response = public_api.request('GET','/api/v1/products?size=1')
    assert response.status_code == 200 and response.headers['X-Sandbox-Mode'] == 'demo-readonly'


@pytest.mark.writes
def test_login_and_current_user(private_api):
    if not all(private_api.credentials.values()):
        pytest.skip('BLOCKED: login credentials unavailable')
    data = private_api.json('POST','/api/v1/auth/login',json=private_api.credentials)
    assert data['token'] and data['tokenType'] == 'Bearer'
    user = private_api.json('GET','/api/v1/auth/me',headers={'Authorization':f"Bearer {data['token']}"})['user']
    assert user['email'] == private_api.credentials['email'] and user['is_active'] is True


@pytest.mark.writes
@pytest.mark.parametrize('case,status', [('missing_email',400),('missing_password',400),('empty_email',400),('empty_password',400),('wrong_password',401),('invalid_email',401)])
def test_login_negative(private_api, case, status):
    if not all(private_api.credentials.values()):
        pytest.skip('BLOCKED: login credentials unavailable')
    payload = dict(private_api.credentials)
    if case.startswith('missing_'): payload.pop(case.removeprefix('missing_'))
    elif case.startswith('empty_'): payload[case.removeprefix('empty_')] = ''
    elif case == 'wrong_password': payload['password'] += '-incorrect'
    else: payload['email'] = 'invalid-email'
    data = private_api.json('POST','/api/v1/auth/login',status=status,json=payload)
    assert data['error']['code'] == ('BAD_REQUEST' if status == 400 else 'UNAUTHORIZED')
    assert 'token' not in data


@pytest.mark.writes
def test_cart_create_retrieve(private_api, cart):
    assert cart['user_id'] is None and cart['guest_token'] and cart['status'] == 'open'
    data=private_api.json('GET',f"/api/v1/carts/{cart['id']}")
    assert data['cart']['id'] == cart['id'] and data['items'] == []
    assert_cart(data)


@pytest.mark.writes
def test_add_and_repeat(private_api, cart, variant):
    path=f"/api/v1/carts/{cart['id']}/items"
    for total in (2,4):
        data=private_api.json('POST',path,status=201,json={'variantId':variant['id'],'qty':2})
        assert len(data['items']) == 1
        item=data['items'][0]
        assert item['qty'] == total and item['product_id'] == variant['product_id']
        assert money(item['unit_price']) == money(variant['price'])
        assert_cart(data)


@pytest.mark.writes
@pytest.mark.parametrize('payload,status,code', [({'qty':0},422,'INVALID_QTY'),({'qty':-1},422,'INVALID_QTY'),({'qty':'abc'},422,'INVALID_QTY'),({'variantId':999999999},404,'NOT_FOUND'),({'variantId':'abc'},422,'INVALID_VARIANT')])
def test_cart_bad_payload(private_api, cart, variant, payload, status, code):
    body={'variantId':variant['id'],'qty':1};body.update(payload)
    data=private_api.json('POST',f"/api/v1/carts/{cart['id']}/items",status=status,json=body)
    assert data['error']['code'] == code
    assert private_api.json('GET',f"/api/v1/carts/{cart['id']}")['items'] == []


@pytest.mark.writes
def test_insufficient_stock(private_api, cart, variant):
    data=private_api.json('POST',f"/api/v1/carts/{cart['id']}/items",status=409,json={'variantId':variant['id'],'qty':variant['available']+1})
    assert data['error']['code'] == 'OUT_OF_STOCK'
    assert private_api.json('GET',f"/api/v1/carts/{cart['id']}")['items'] == []


@pytest.mark.writes
@pytest.mark.parametrize('identifier,status', [('abc',400),('999999999',404)])
def test_cart_invalid_id(private_api,identifier,status):
    assert private_api.json('GET',f'/api/v1/carts/{identifier}',status=status)['error']['code']


@pytest.mark.writes
def test_sandbox_isolation(private_api, cart):
    other=ApiClient(writable=True)
    try:
        fresh=other.json('POST','/api/v1/sandbox',status=201,json={'label':'QualityHub isolation peer'})
        other.session.headers['X-Sandbox-Key']=fresh['apiKey']
        assert other.json('GET',f"/api/v1/carts/{cart['id']}",status=404)['error']['code']=='NOT_FOUND'
    finally:
        other.close()
