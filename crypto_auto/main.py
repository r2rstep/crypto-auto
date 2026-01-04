import asyncio
import sys
from datetime import datetime, timezone
import structlog
from crypto_auto.config.loader import load_crypto_projects, ConfigurationError
from crypto_auto.config.settings import settings
from crypto_auto.api.defillama import DeFiLlamaClient
from crypto_auto.api.github_api import GitHubClient
from crypto_auto.models.analysis import ProjectAnalysis
from crypto_auto.analysis.fdv_analyzer import FDVAnalyzer
from crypto_auto.analysis.rebalancer import PortfolioRebalancer
from crypto_auto.outputs.console import (
    print_portfolio_analysis,
    print_rebalance_recommendations,
    print_summary_stats,
)
from crypto_auto.outputs.json_writer import write_analysis_json

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def analyze_project(
    project_config, defillama_client: DeFiLlamaClient, github_client: GitHubClient
) -> ProjectAnalysis | None:
    logger.info("analyzing_project", ticker=project_config.ticker)

    try:
        market_data = await defillama_client.get_market_data(project_config.defillama_slug)

        total_commits = 0
        for repo in project_config.github_repos:
            commits = await github_client.get_commit_activity(
                repo, days=settings.dev_activity_lookback_days
            )
            total_commits += commits

        analysis = ProjectAnalysis(
            project=project_config,
            market_data=market_data,
            dev_commits_30d=total_commits,
            health_status="OK",
        )

        fdv_health = FDVAnalyzer.analyze_fdv_health(market_data)
        analysis.fdv_health = fdv_health

        analysis.calculate_health(settings.fdv_ratio_warning_threshold)

        logger.info(
            "project_analyzed",
            ticker=project_config.ticker,
            health_status=analysis.health_status,
            fdv_ratio=market_data.mcap_fdv_ratio,
            commits=total_commits,
        )

        return analysis

    except Exception as e:
        logger.error(
            "project_analysis_failed",
            ticker=project_config.ticker,
            error=str(e),
            exc_info=True,
        )
        return None


async def main():
    logger.info("crypto_auto_started", timestamp=datetime.now(timezone.utc).isoformat())

    try:
        projects = load_crypto_projects()
        logger.info("projects_loaded", count=len(projects))
    except ConfigurationError as e:
        logger.error("configuration_error", error=str(e))
        print(f"❌ Configuration error: {e}")
        return 1

    async with DeFiLlamaClient() as defillama_client, GitHubClient() as github_client:
        tasks = [
            analyze_project(project, defillama_client, github_client) for project in projects
        ]
        results = await asyncio.gather(*tasks)

    analyzed_projects = [r for r in results if r is not None]

    if not analyzed_projects:
        logger.error("no_projects_analyzed")
        print("❌ Failed to analyze any projects")
        return 1

    if len(analyzed_projects) < len(projects):
        logger.warning(
            "partial_analysis",
            analyzed=len(analyzed_projects),
            total=len(projects),
        )

    print_portfolio_analysis(analyzed_projects)
    print_summary_stats(analyzed_projects)

    current_holdings = {p.project.ticker: 0.0 for p in analyzed_projects}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations_raw = rebalancer.calculate_purchase_recommendations(analyzed_projects)
    recommendations = PortfolioRebalancer.format_recommendations(
        recommendations_raw, analyzed_projects
    )

    print_rebalance_recommendations(recommendations)

    output_path = write_analysis_json(analyzed_projects, recommendations)
    print(f"📊 Analysis saved to: {output_path}")

    logger.info("crypto_auto_completed", projects_analyzed=len(analyzed_projects))
    return 0


def cli():
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("interrupted_by_user")
        print("\n👋 Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("unexpected_error", error=str(e), exc_info=True)
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
