from typing import Literal
from pydantic import BaseModel, Field, field_validator


class CryptoProject(BaseModel):
    ticker: str = Field(..., description="Cryptocurrency ticker symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Full project name")
    defillama_slug: str = Field(..., description="DeFiLlama API identifier")
    github_repos: list[str] = Field(
        default_factory=list, description="List of GitHub repos (format: owner/repo)"
    )
    category: Literal["core", "midcap", "experimental"] = Field(
        ..., description="Investment category"
    )
    target_allocation: float = Field(
        ..., ge=0.0, le=1.0, description="Target portfolio allocation (0.0-1.0)"
    )

    @field_validator("ticker")
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()

    @field_validator("github_repos")
    @classmethod
    def validate_github_repos(cls, v: list[str]) -> list[str]:
        for repo in v:
            if "/" not in repo or len(repo.split("/")) != 2:
                raise ValueError(f"Invalid GitHub repo format: {repo}. Expected 'owner/repo'")
        return v
