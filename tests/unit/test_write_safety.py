"""Safety gates must reject unsafe writes before network access."""
import pytest
from clients.api import ApiClient


@pytest.mark.parametrize('url,writable',[('https://example.com',True),('http://localhost:4001',True),('http://localhost:4000',False)])
def test_unsafe_write_rejected(url,writable):
    client=ApiClient(base_url=url,writable=writable)
    try:
        with pytest.raises(RuntimeError,match='authorized local'):
            client.request('POST','/api/v1/carts')
    finally:
        client.close()
