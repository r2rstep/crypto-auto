# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cryptocurrency portfolio automation system designed to run with zero cost using free tiers of various services. The system automates data collection, analysis, and portfolio rebalancing recommendations.

**Core Architecture:**
- **Data Collection**: Python scripts running on GitHub Actions (weekly schedule) to fetch:
  - Market data and FDV (Fully Diluted Valuation) from DeFiLlama API
  - Developer activity from GitHub API
- **Sentiment Analysis**: Make.com scenarios processing newsletters via Gemini 1.5 Flash API
- **Central Dashboard**: Google Sheets serving as the source of truth for all data and recommendations
- **Automation Strategy**: 80/20 rule - automate 80% of repetitive work (data), leave 20% for human decision-making

**Investment Strategy (from docs):**
- 70% core holdings (BTC/ETH)
- 20% mid-cap projects (validated with FDV checks)
- 10% experimental/new projects
- Monthly DCA (Dollar Cost Averaging)
- Rebalancing via additions (not sales) to avoid tax events

## Key Technical Decisions

**FDV Monitoring**: Critical filter to avoid VC-inflated projects. Target projects where Market Cap is at least 40-50% of FDV to avoid dilution risk.

**Developer Activity Tracking**: Monitor GitHub commit activity as a leading indicator of project health, independent of price action.

**Rebalancing via Additions**: Instead of selling appreciated assets, new DCA contributions are allocated to underweight positions to maintain target allocations while minimizing tax events.

## Development Commands

**Environment Management:**
- Uses `uv` for Python dependency management
- Python 3.12+ required

**Testing:**
- Run tests with: `pytest ...`
- Use PyCharm's MCP server for test execution

**Quality Checks:**
- Use `pre-commit` for all quality checks except mypy
- Only add newly created files to git with `git add`

## Project Structure

```
/crypto-auto/        - Main application code
/tests/              - Test suite
/docs/               - Polish documentation with strategy and automation plans
  Automatyzacja.md   - Complete automation system design with sequence diagrams
  Strategia.md       - Investment strategy and source analysis
  arkusz analizy.md  - Google Sheets structure and rebalancing formulas
```

## External Integrations (Planned)

**Free Services:**
- DeFiLlama API (no key required) - market cap and FDV data
- GitHub API (free Personal Access Token) - developer activity
- Make.com (free tier) - newsletter processing automation
- Gemini 1.5 Flash API (free tier) - sentiment analysis
- Google Sheets API - data storage and dashboard
- GitHub Actions - weekly scheduled execution

**Data Sources:**
- RealVision/Glassnode newsletters - institutional insights
- Kanga Exchange newsletter - Polish market news
- Coinrule/Chainspect - technical trends

## Code Style

- Add comments only when code is not self-explanatory
- Add docstrings only when code is not self-explanatory
- Do not implement dry-run modes