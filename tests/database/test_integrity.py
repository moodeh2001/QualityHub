"""Read-only existing-data audits; never mistaken for write rejection tests."""
from pathlib import Path
import pytest

pytestmark=pytest.mark.database
SQL=Path(__file__).resolve().parents[2]/'sql'


@pytest.mark.parametrize('case',['001','002','003','006','007','008','009','010','012'])
def test_integrity(db,case):
    query=next(SQL.glob(f'DB-TC-{case}*')).read_text(encoding='utf-8')
    if case=='009': query=query.split('-- The original synthetic')[0]
    rows=db.execute(query).fetchall()
    assert not rows, f'DB-TC-{case}: {len(rows)} invalid existing records (identifiers redacted)'


def test_inventory(db):
    rows=db.execute('SELECT variant_id FROM public.inventory WHERE stock_qty<0 OR reserved_qty<0 OR reserved_qty>stock_qty').fetchall()
    assert not rows, f'{len(rows)} invalid inventory rows'


def test_constraints_catalog(db):
    rows=db.execute("SELECT conrelid::regclass::text AS table_name, contype, pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE connamespace='public'::regnamespace").fetchall()
    for table,kind,fragment in [('cart_items','c','qty > 0'),('cart_items','u','cart_id, variant_id'),('users','u','sandbox_id, email'),('payments','f','REFERENCES orders'),('product_variants','f','REFERENCES products')]:
        assert any(r['table_name']==table and r['contype']==kind and fragment in r['definition'] for r in rows), f'Missing expected {kind} constraint on {table}'
