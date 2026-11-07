"""Controlled private API operations reconciled against read-only SQL."""
import json
from pathlib import Path
import pytest
from clients.api import assert_cart,money

pytestmark=[pytest.mark.integration,pytest.mark.writes]


def test_cart_creation(db,private_api,cart):
    row=db.execute('SELECT id,sandbox_id,user_id,status FROM public.carts WHERE id=%s',(cart['id'],)).fetchone()
    assert row and str(row['sandbox_id'])==private_api.sandbox_id
    assert row['user_id'] is None and row['status']=='open'


def test_add_repeat_and_pricing(db,private_api,cart,variant):
    for quantity in (2,4):
        data=private_api.json('POST',f"/api/v1/carts/{cart['id']}/items",status=201,json={'variantId':variant['id'],'qty':2})
        rows=db.execute('SELECT variant_id,qty,unit_price_snapshot,sandbox_id FROM public.cart_items WHERE cart_id=%s',(cart['id'],)).fetchall()
        assert len(rows)==1 and rows[0]['qty']==quantity
        assert rows[0]['variant_id']==variant['id'] and str(rows[0]['sandbox_id'])==private_api.sandbox_id
        assert money(rows[0]['unit_price_snapshot'])==money(data['items'][0]['unit_price'])
        assert_cart(data)
        folder=Path(__file__).resolve().parents[2]/'sql'
        for case in ('004','005','011'):
            path=next(folder.glob(f'DB-TC-{case}*'))
            query=path.read_text(encoding='utf-8').replace(":'api_cart'",'%s')
            assert not db.execute(query,(json.dumps(data),)).fetchall(), f'DB-TC-{case} mismatch'
        calc=db.execute('SELECT coalesce(sum(qty*unit_price_snapshot),0) AS subtotal FROM public.cart_items WHERE cart_id=%s',(cart['id'],)).fetchone()
        assert money(calc['subtotal'])==money(data['totals']['subtotal'])


def test_database_sandbox_boundary(db,private_api,cart):
    rows = db.execute('SELECT sandbox_id FROM public.carts WHERE id=%s', (cart['id'],)).fetchall()
    assert len(rows) == 1 and str(rows[0]['sandbox_id']) == private_api.sandbox_id
    assert db.execute('SELECT count(*) AS n FROM public.carts WHERE id=%s AND sandbox_id<>%s',(cart['id'],private_api.sandbox_id)).fetchone()['n']==0
