import pytest
from crypto_auto.analysis.fdv_analyzer import FDVAnalyzer
from crypto_auto.models.market_data import MarketData


def test_fdv_analyzer_excellent():
    market_data = MarketData(
        ticker="BTC",
        price=95000,
        market_cap=1_800_000_000_000,
        fdv=1_850_000_000_000,
        mcap_fdv_ratio=0.973,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.status == "EXCELLENT"
    assert result.severity == "LOW"
    assert result.ratio == 0.973
    assert "Minimal dilution" in result.message


def test_fdv_analyzer_healthy():
    market_data = MarketData(
        ticker="TEST",
        price=100,
        market_cap=475_000_000,
        fdv=1_000_000_000,
        mcap_fdv_ratio=0.475,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.status == "HEALTHY"
    assert result.severity == "LOW"
    assert result.ratio == 0.475


def test_fdv_analyzer_caution():
    market_data = MarketData(
        ticker="TEST",
        price=100,
        market_cap=425_000_000,
        fdv=1_000_000_000,
        mcap_fdv_ratio=0.425,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.status == "CAUTION"
    assert result.severity == "MEDIUM"
    assert result.ratio == 0.425
    assert "Below target range" in result.message


def test_fdv_analyzer_warning():
    market_data = MarketData(
        ticker="TEST",
        price=100,
        market_cap=300_000_000,
        fdv=1_000_000_000,
        mcap_fdv_ratio=0.3,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.status == "WARNING"
    assert result.severity == "HIGH"
    assert result.ratio == 0.3
    assert "High dilution risk" in result.message


def test_fdv_analyzer_boundary_warning():
    market_data = MarketData(
        ticker="TEST",
        price=100,
        market_cap=399_999_999,
        fdv=1_000_000_000,
        mcap_fdv_ratio=0.399999999,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.status == "WARNING"


def test_fdv_analyzer_zero_fdv():
    market_data = MarketData(
        ticker="TEST",
        price=100,
        market_cap=0,
        fdv=0,
        mcap_fdv_ratio=0,
    )

    result = FDVAnalyzer.analyze_fdv_health(market_data)

    assert result.ratio == 0
    assert result.status == "WARNING"
