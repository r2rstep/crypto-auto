from pydantic import BaseModel, Field, field_validator


class MarketData(BaseModel):
    ticker: str = Field(..., description="Cryptocurrency ticker symbol")
    price: float = Field(..., ge=0, description="Current price in USD")
    market_cap: float = Field(..., ge=0, description="Market capitalization in USD")
    fdv: float = Field(..., ge=0, description="Fully Diluted Valuation in USD")
    mcap_fdv_ratio: float = Field(
        ..., ge=0, le=1, description="Market Cap to FDV ratio (0.0-1.0)"
    )

    @field_validator("mcap_fdv_ratio", mode="before")
    @classmethod
    def calculate_ratio(cls, v: float | None, info) -> float:
        if v is not None:
            return v

        values = info.data
        fdv = values.get("fdv", 0)
        market_cap = values.get("market_cap", 0)

        if fdv == 0:
            return 0.0

        ratio = market_cap / fdv
        return min(ratio, 1.0)

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()
