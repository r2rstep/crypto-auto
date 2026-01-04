import structlog
from crypto_auto.api.base import BaseAPIClient, APIError
from crypto_auto.models.market_data import MarketData

logger = structlog.get_logger()


class DeFiLlamaClient(BaseAPIClient):
    def __init__(self):
        super().__init__(base_url="https://api.llama.fi")

    async def get_market_data(self, slug: str) -> MarketData:
        endpoint = f"/protocol/{slug}"
        data = await self.get(endpoint)

        ticker = slug.upper()

        mcap = data.get("mcap") or data.get("tvl") or 0
        fdv = data.get("fdv") or data.get("fdvTvl")

        if fdv is None:
            fdv = mcap * 1.5
            logger.warning(
                "fdv_not_available",
                slug=slug,
                message="FDV not provided by API, estimating as 1.5x market cap",
            )

        price = data.get("price", 0)

        if mcap == 0 and fdv == 0:
            raise APIError(f"No market data available for {slug}")

        logger.info(
            "market_data_fetched",
            ticker=ticker,
            mcap=mcap,
            fdv=fdv,
            price=price,
        )

        return MarketData(
            ticker=ticker,
            price=price,
            market_cap=mcap,
            fdv=fdv,
            mcap_fdv_ratio=mcap / fdv if fdv > 0 else 0,
        )
