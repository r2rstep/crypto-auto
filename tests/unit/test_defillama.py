import pytest
import respx
import httpx
from crypto_auto.api.defillama import DeFiLlamaClient
from crypto_auto.api.base import APIError


@pytest.mark.asyncio
async def test_defillama_get_market_data_success(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/bitcoin").mock(
        return_value=httpx.Response(
            200,
            json={
                "mcap": 1_800_000_000_000,
                "fdv": 1_850_000_000_000,
                "price": 95000.0,
            },
        )
    )

    async with DeFiLlamaClient() as client:
        market_data = await client.get_market_data("bitcoin")

    assert market_data.ticker == "BITCOIN"
    assert market_data.price == 95000.0
    assert market_data.market_cap == 1_800_000_000_000
    assert market_data.fdv == 1_850_000_000_000
    assert market_data.mcap_fdv_ratio == pytest.approx(0.973, rel=0.001)


@pytest.mark.asyncio
async def test_defillama_missing_fdv(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/test-token").mock(
        return_value=httpx.Response(
            200,
            json={
                "mcap": 1_000_000_000,
                "price": 100.0,
            },
        )
    )

    async with DeFiLlamaClient() as client:
        market_data = await client.get_market_data("test-token")

    assert market_data.ticker == "TEST-TOKEN"
    assert market_data.market_cap == 1_000_000_000
    assert market_data.fdv == 1_500_000_000
    assert market_data.price == 100.0


@pytest.mark.asyncio
async def test_defillama_alternative_fields(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/test").mock(
        return_value=httpx.Response(
            200,
            json={
                "tvl": 500_000_000,
                "fdvTvl": 600_000_000,
                "price": 50.0,
            },
        )
    )

    async with DeFiLlamaClient() as client:
        market_data = await client.get_market_data("test")

    assert market_data.market_cap == 500_000_000
    assert market_data.fdv == 600_000_000


@pytest.mark.asyncio
async def test_defillama_no_data(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/invalid").mock(
        return_value=httpx.Response(200, json={})
    )

    async with DeFiLlamaClient() as client:
        with pytest.raises(APIError, match="No market data available"):
            await client.get_market_data("invalid")


@pytest.mark.asyncio
async def test_defillama_http_404(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/nonexistent").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )

    async with DeFiLlamaClient() as client:
        with pytest.raises(APIError, match="HTTP 404"):
            await client.get_market_data("nonexistent")


@pytest.mark.asyncio
async def test_defillama_invalid_json(respx_mock):
    respx_mock.get("https://api.llama.fi/protocol/broken").mock(
        return_value=httpx.Response(200, content=b"invalid json{")
    )

    async with DeFiLlamaClient() as client:
        with pytest.raises(APIError, match="Invalid JSON response"):
            await client.get_market_data("broken")
