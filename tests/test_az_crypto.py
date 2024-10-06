import pytest

from azimuth import az


def test_az_import_error():
    with pytest.raises(AttributeError, match="'az' has no extension 'bad_extension'"):
        assert not az.bad_extension
    assert az.crypto


def test_az_crypto_import_error():
    with pytest.raises(AttributeError, match="extension 'az.crypto' has no attribute 'bad_module'"):
        assert not az.crypto.bad_module
    assert az.crypto.candles


def test_az_crypto_provider_error():
    with pytest.raises(AttributeError, match="provider 'bad_provider' has no found"):
        assert not az.crypto.candles('BTC/USDT', provider="bad_provider")
    assert az.crypto.candles('BTC/USDT', provider="binance")


@pytest.mark.asyncio
async def test_az_crypto_candles():
    aiter_ = az.crypto.candles('BTC/USDT', provider="binance:spot", interval="1d", start_date="2024-01-01")
    adata = [item.model_dump() async for item in aiter_]
    assert adata and len(adata) > 200

    iter_ = az.crypto.candles('BTC/USDT', provider="binance:spot", interval="1d", start_date="2024-01-01")
    data = [item.model_dump() for item in iter_]
    assert adata[:-1] == data[:-1]

@pytest.mark.asyncio
async def test_az_crypto_candles_many():
    b_iter = az.crypto.candles('BTC/USDT', provider="binance:spot", interval="1d",
                               start_date="2024-01-01", end_date="2024-01-31")
    m_iter = az.crypto.candles('BTC/USDT', provider="mexc:spot", interval="1d",
                               start_date="2024-01-01", end_date="2024-01-31")

    assert len(tuple(b_iter)) == len(tuple(m_iter)) == 31

