import structlog
from crypto_auto.models.market_data import MarketData
from crypto_auto.models.analysis import FDVHealthStatus
from crypto_auto.config.settings import settings

logger = structlog.get_logger()


class FDVAnalyzer:
    @staticmethod
    def analyze_fdv_health(market_data: MarketData) -> FDVHealthStatus:
        ratio = market_data.mcap_fdv_ratio

        if ratio < settings.fdv_ratio_warning_threshold:
            status = "WARNING"
            message = f"High dilution risk: MCap is only {ratio:.1%} of FDV"
            severity = "HIGH"
        elif ratio < settings.fdv_ratio_target_min:
            status = "CAUTION"
            message = f"Below target range: {ratio:.1%} < {settings.fdv_ratio_target_min:.1%}"
            severity = "MEDIUM"
        elif ratio <= settings.fdv_ratio_target_max:
            status = "HEALTHY"
            message = f"Within target range: {ratio:.1%}"
            severity = "LOW"
        else:
            status = "EXCELLENT"
            message = f"Minimal dilution: {ratio:.1%}"
            severity = "LOW"

        logger.info(
            "fdv_health_analyzed",
            ticker=market_data.ticker,
            ratio=ratio,
            status=status,
            severity=severity,
        )

        return FDVHealthStatus(
            status=status,
            message=message,
            severity=severity,
            ratio=ratio,
        )
