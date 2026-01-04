from typing import Literal
from pydantic import BaseModel, Field
from crypto_auto.models.crypto import CryptoProject
from crypto_auto.models.market_data import MarketData


class FDVHealthStatus(BaseModel):
    status: Literal["WARNING", "CAUTION", "HEALTHY", "EXCELLENT"]
    message: str
    severity: Literal["HIGH", "MEDIUM", "LOW"]
    ratio: float


class ProjectAnalysis(BaseModel):
    project: CryptoProject
    market_data: MarketData
    dev_commits_30d: int = Field(..., ge=0, description="Number of commits in last 30 days")
    dev_activity_change: float | None = Field(
        None, description="Percentage change in dev activity from previous period"
    )
    health_status: Literal["OK", "FDV_WARNING", "LOW_ACTIVITY"]
    fdv_health: FDVHealthStatus | None = None

    def calculate_health(self, fdv_warning_threshold: float, min_commits: int = 10) -> None:
        if self.market_data.mcap_fdv_ratio < fdv_warning_threshold:
            self.health_status = "FDV_WARNING"
        elif self.dev_commits_30d < min_commits:
            self.health_status = "LOW_ACTIVITY"
        else:
            self.health_status = "OK"


class PortfolioSnapshot(BaseModel):
    timestamp: str
    projects: list[ProjectAnalysis]
    total_market_cap: float = Field(..., ge=0)

    def get_fdv_warnings(self) -> list[ProjectAnalysis]:
        return [p for p in self.projects if p.health_status == "FDV_WARNING"]

    def get_low_activity_projects(self) -> list[ProjectAnalysis]:
        return [p for p in self.projects if p.health_status == "LOW_ACTIVITY"]
