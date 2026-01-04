import structlog
from crypto_auto.models.analysis import ProjectAnalysis

logger = structlog.get_logger()


class PortfolioRebalancer:
    def __init__(self, current_holdings: dict[str, float], dca_amount: float):
        self.current_holdings = current_holdings
        self.dca_amount = dca_amount

    def calculate_purchase_recommendations(
        self, projects: list[ProjectAnalysis]
    ) -> dict[str, float]:
        total_value = sum(self.current_holdings.values()) + self.dca_amount

        logger.info(
            "calculating_rebalance",
            current_total=sum(self.current_holdings.values()),
            dca_amount=self.dca_amount,
            new_total=total_value,
        )

        recommendations = {}

        for project in projects:
            ticker = project.project.ticker
            target_allocation = project.project.target_allocation
            target_value = total_value * target_allocation
            current_value = self.current_holdings.get(ticker, 0)

            gap = max(0, target_value - current_value)
            recommendations[ticker] = gap

            logger.debug(
                "allocation_calculated",
                ticker=ticker,
                target_allocation=target_allocation,
                current_value=current_value,
                target_value=target_value,
                gap=gap,
            )

        total_gap = sum(recommendations.values())

        if total_gap > 0:
            scale_factor = self.dca_amount / total_gap
            recommendations = {ticker: amount * scale_factor for ticker, amount in recommendations.items()}

            logger.info(
                "rebalance_scaled",
                total_gap=total_gap,
                scale_factor=scale_factor,
                recommendations=recommendations,
            )
        else:
            logger.info(
                "portfolio_balanced",
                message="All positions at or above target allocation",
            )

        return recommendations

    @staticmethod
    def format_recommendations(
        recommendations: dict[str, float], projects: list[ProjectAnalysis]
    ) -> list[dict[str, str | float]]:
        project_map = {p.project.ticker: p for p in projects}

        formatted = []
        for ticker, amount in recommendations.items():
            if amount > 0:
                project = project_map[ticker]
                formatted.append(
                    {
                        "ticker": ticker,
                        "amount_usd": round(amount, 2),
                        "current_price": project.market_data.price,
                        "quantity": round(amount / project.market_data.price, 8)
                        if project.market_data.price > 0
                        else 0,
                    }
                )

        formatted.sort(key=lambda x: x["amount_usd"], reverse=True)
        return formatted
