import pytest
import respx
import httpx
import json
from pathlib import Path
from crypto_auto.main import main
from crypto_auto.config.loader import load_crypto_projects


@pytest.mark.asyncio
async def test_main_flow_success(temp_cryptos_json, tmp_path, monkeypatch, respx_mock):
    monkeypatch.chdir(temp_cryptos_json.parent)

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

    respx_mock.get("https://api.llama.fi/protocol/ethereum").mock(
        return_value=httpx.Response(
            200,
            json={
                "mcap": 500_000_000_000,
                "fdv": 550_000_000_000,
                "price": 4200.0,
            },
        )
    )

    respx_mock.get("https://api.github.com/repos/bitcoin/bitcoin/commits").mock(
        return_value=httpx.Response(200, json=[{"sha": f"sha{i}"} for i in range(50)])
    )

    respx_mock.get("https://api.github.com/repos/ethereum/go-ethereum/commits").mock(
        return_value=httpx.Response(200, json=[{"sha": f"sha{i}"} for i in range(75)])
    )

    exit_code = await main()

    assert exit_code == 0

    analysis_files = list(Path.cwd().glob("analysis_*.json"))
    assert len(analysis_files) == 1

    with open(analysis_files[0]) as f:
        data = json.load(f)

    assert "projects" in data
    assert len(data["projects"]) == 2
    assert "rebalance_recommendations" in data
    assert "summary" in data

    btc_project = next(p for p in data["projects"] if p["ticker"] == "BTC")
    assert btc_project["dev_commits_30d"] == 50
    assert btc_project["market_data"]["price"] == 95000.0

    eth_project = next(p for p in data["projects"] if p["ticker"] == "ETH")
    assert eth_project["dev_commits_30d"] == 75


@pytest.mark.asyncio
async def test_main_flow_partial_failure(temp_cryptos_json, monkeypatch, respx_mock):
    monkeypatch.chdir(temp_cryptos_json.parent)

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

    respx_mock.get("https://api.llama.fi/protocol/ethereum").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )

    respx_mock.get("https://api.github.com/repos/bitcoin/bitcoin/commits").mock(
        return_value=httpx.Response(200, json=[{"sha": f"sha{i}"} for i in range(50)])
    )

    exit_code = await main()

    assert exit_code == 0

    analysis_files = list(Path.cwd().glob("analysis_*.json"))
    assert len(analysis_files) == 1

    with open(analysis_files[0]) as f:
        data = json.load(f)

    assert len(data["projects"]) == 1
    assert data["projects"][0]["ticker"] == "BTC"


@pytest.mark.asyncio
async def test_main_flow_missing_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    exit_code = await main()

    assert exit_code == 1


@pytest.mark.asyncio
async def test_load_crypto_projects_success(temp_cryptos_json):
    projects = load_crypto_projects(temp_cryptos_json)

    assert len(projects) == 2
    assert projects[0].ticker == "BTC"
    assert projects[1].ticker == "ETH"
    assert projects[0].target_allocation == 0.50
    assert projects[1].target_allocation == 0.50


def test_load_crypto_projects_missing_file(tmp_path):
    from crypto_auto.config.loader import ConfigurationError

    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        load_crypto_projects(tmp_path / "nonexistent.json")


def test_load_crypto_projects_invalid_json(tmp_path):
    from crypto_auto.config.loader import ConfigurationError

    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{ invalid json")

    with pytest.raises(ConfigurationError, match="Invalid JSON"):
        load_crypto_projects(invalid_file)


def test_load_crypto_projects_missing_projects_key(tmp_path):
    from crypto_auto.config.loader import ConfigurationError

    invalid_file = tmp_path / "no_projects.json"
    invalid_file.write_text('{"other_key": []}')

    with pytest.raises(ConfigurationError, match="Missing 'projects' key"):
        load_crypto_projects(invalid_file)


def test_load_crypto_projects_invalid_allocation(tmp_path):
    from crypto_auto.config.loader import ConfigurationError

    invalid_file = tmp_path / "bad_allocation.json"
    data = {
        "projects": [
            {
                "ticker": "BTC",
                "name": "Bitcoin",
                "defillama_slug": "bitcoin",
                "github_repos": ["bitcoin/bitcoin"],
                "category": "core",
                "target_allocation": 0.30,
            },
            {
                "ticker": "ETH",
                "name": "Ethereum",
                "defillama_slug": "ethereum",
                "github_repos": ["ethereum/go-ethereum"],
                "category": "core",
                "target_allocation": 0.30,
            },
        ]
    }

    with open(invalid_file, "w") as f:
        json.dump(data, f)

    with pytest.raises(ConfigurationError, match="Total target allocation"):
        load_crypto_projects(invalid_file)
