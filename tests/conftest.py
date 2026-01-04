import pytest
from crypto_auto.models.crypto import CryptoProject
from crypto_auto.models.market_data import MarketData
from crypto_auto.models.analysis import ProjectAnalysis, FDVHealthStatus


@pytest.fixture
def sample_crypto_project():
    return CryptoProject(
        ticker="BTC",
        name="Bitcoin",
        defillama_slug="bitcoin",
        github_repos=["bitcoin/bitcoin"],
        category="core",
        target_allocation=0.50,
    )


@pytest.fixture
def sample_market_data():
    return MarketData(
        ticker="BTC",
        price=95000.0,
        market_cap=1_800_000_000_000,
        fdv=1_850_000_000_000,
        mcap_fdv_ratio=0.973,
    )


@pytest.fixture
def sample_fdv_health():
    return FDVHealthStatus(
        status="EXCELLENT",
        message="Minimal dilution: 97.3%",
        severity="LOW",
        ratio=0.973,
    )


@pytest.fixture
def sample_project_analysis(sample_crypto_project, sample_market_data, sample_fdv_health):
    return ProjectAnalysis(
        project=sample_crypto_project,
        market_data=sample_market_data,
        dev_commits_30d=150,
        health_status="OK",
        fdv_health=sample_fdv_health,
    )


@pytest.fixture
def temp_cryptos_json(tmp_path):
    import json

    cryptos_file = tmp_path / "cryptos.json"
    data = {
        "projects": [
            {
                "ticker": "BTC",
                "name": "Bitcoin",
                "defillama_slug": "bitcoin",
                "github_repos": ["bitcoin/bitcoin"],
                "category": "core",
                "target_allocation": 0.50,
            },
            {
                "ticker": "ETH",
                "name": "Ethereum",
                "defillama_slug": "ethereum",
                "github_repos": ["ethereum/go-ethereum"],
                "category": "core",
                "target_allocation": 0.50,
            },
        ]
    }

    with open(cryptos_file, "w") as f:
        json.dump(data, f)

    return cryptos_file
