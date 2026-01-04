import pytest
from crypto_auto.analysis.rebalancer import PortfolioRebalancer
from crypto_auto.models.crypto import CryptoProject
from crypto_auto.models.market_data import MarketData
from crypto_auto.models.analysis import ProjectAnalysis


@pytest.fixture
def sample_projects():
    btc_project = CryptoProject(
        ticker="BTC",
        name="Bitcoin",
        defillama_slug="bitcoin",
        github_repos=["bitcoin/bitcoin"],
        category="core",
        target_allocation=0.60,
    )

    eth_project = CryptoProject(
        ticker="ETH",
        name="Ethereum",
        defillama_slug="ethereum",
        github_repos=["ethereum/go-ethereum"],
        category="core",
        target_allocation=0.40,
    )

    btc_analysis = ProjectAnalysis(
        project=btc_project,
        market_data=MarketData(
            ticker="BTC",
            price=95000.0,
            market_cap=1_800_000_000_000,
            fdv=1_850_000_000_000,
            mcap_fdv_ratio=0.973,
        ),
        dev_commits_30d=150,
        health_status="OK",
    )

    eth_analysis = ProjectAnalysis(
        project=eth_project,
        market_data=MarketData(
            ticker="ETH",
            price=4200.0,
            market_cap=500_000_000_000,
            fdv=550_000_000_000,
            mcap_fdv_ratio=0.909,
        ),
        dev_commits_30d=200,
        health_status="OK",
    )

    return [btc_analysis, eth_analysis]


def test_rebalancer_empty_portfolio(sample_projects):
    current_holdings = {"BTC": 0.0, "ETH": 0.0}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations = rebalancer.calculate_purchase_recommendations(sample_projects)

    assert recommendations["BTC"] == pytest.approx(600.0, rel=0.01)
    assert recommendations["ETH"] == pytest.approx(400.0, rel=0.01)


def test_rebalancer_underweight_eth(sample_projects):
    current_holdings = {"BTC": 6000.0, "ETH": 1000.0}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations = rebalancer.calculate_purchase_recommendations(sample_projects)

    total = sum(current_holdings.values()) + dca_amount
    assert total == 8000.0
    assert recommendations["ETH"] > recommendations["BTC"]


def test_rebalancer_balanced_portfolio(sample_projects):
    current_holdings = {"BTC": 9600.0, "ETH": 6400.0}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations = rebalancer.calculate_purchase_recommendations(sample_projects)

    assert recommendations["BTC"] == pytest.approx(600.0, rel=0.01)
    assert recommendations["ETH"] == pytest.approx(400.0, rel=0.01)


def test_rebalancer_format_recommendations(sample_projects):
    current_holdings = {"BTC": 0.0, "ETH": 0.0}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations_raw = rebalancer.calculate_purchase_recommendations(sample_projects)
    formatted = PortfolioRebalancer.format_recommendations(recommendations_raw, sample_projects)

    assert len(formatted) == 2
    assert formatted[0]["ticker"] in ["BTC", "ETH"]
    assert "amount_usd" in formatted[0]
    assert "current_price" in formatted[0]
    assert "quantity" in formatted[0]

    btc_rec = next(r for r in formatted if r["ticker"] == "BTC")
    assert btc_rec["current_price"] == 95000.0
    assert btc_rec["quantity"] > 0


def test_rebalancer_single_project_underweight():
    project = CryptoProject(
        ticker="BTC",
        name="Bitcoin",
        defillama_slug="bitcoin",
        github_repos=["bitcoin/bitcoin"],
        category="core",
        target_allocation=1.0,
    )

    analysis = ProjectAnalysis(
        project=project,
        market_data=MarketData(
            ticker="BTC",
            price=95000.0,
            market_cap=1_800_000_000_000,
            fdv=1_850_000_000_000,
            mcap_fdv_ratio=0.973,
        ),
        dev_commits_30d=150,
        health_status="OK",
    )

    current_holdings = {"BTC": 5000.0}
    dca_amount = 1000.0

    rebalancer = PortfolioRebalancer(current_holdings, dca_amount)
    recommendations = rebalancer.calculate_purchase_recommendations([analysis])

    assert recommendations["BTC"] == pytest.approx(1000.0, rel=0.01)
