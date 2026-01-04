# Crypto Portfolio Automation

Automated cryptocurrency portfolio analysis and rebalancing system that runs on zero-cost infrastructure using GitHub Actions, DeFiLlama API, and GitHub API.

## Features

- **Automated Data Collection**: Weekly market data (FDV, market cap, price) from DeFiLlama
- **Developer Activity Tracking**: Monitor GitHub commit activity as a project health indicator
- **FDV Analysis**: Identify projects with high dilution risk (MCap/FDV ratio analysis)
- **Rebalancing via Additions**: Calculate DCA allocations to maintain target portfolio weights without selling
- **Rich Console Output**: Formatted tables with color-coded health indicators
- **JSON Export**: Timestamped analysis results for tracking and integration
- **Comprehensive Testing**: >90% code coverage with unit and integration tests

## Investment Strategy

The system implements a conservative DCA strategy:
- **70% Core Holdings**: Bitcoin and Ethereum
- **20% Mid-Cap Projects**: Validated with FDV and developer activity checks
- **10% Experimental**: Higher-risk newer projects

**Key Metrics**:
- FDV Ratio: Target MCap ≥ 40-50% of FDV to avoid VC dilution
- Developer Activity: 30-day commit counts as leading indicator

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub Personal Access Token ([create here](https://github.com/settings/tokens))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/crypto-auto.git
cd crypto-auto

# Install dependencies with uv
uv sync

# Copy environment template
cp .env.example .env

# Edit .env and add your GitHub token
nano .env
```

### Configuration

#### 1. Set Environment Variables

Edit `.env`:

```bash
GITHUB_TOKEN=ghp_your_personal_access_token_here
FDV_RATIO_WARNING_THRESHOLD=0.4
DEV_ACTIVITY_LOOKBACK_DAYS=30
LOG_LEVEL=INFO
```

#### 2. Configure Projects to Track

Edit `cryptos.json`:

```json
{
  "projects": [
    {
      "ticker": "BTC",
      "name": "Bitcoin",
      "defillama_slug": "bitcoin",
      "github_repos": ["bitcoin/bitcoin"],
      "category": "core",
      "target_allocation": 0.50
    },
    {
      "ticker": "ETH",
      "name": "Ethereum",
      "defillama_slug": "ethereum",
      "github_repos": ["ethereum/go-ethereum"],
      "category": "core",
      "target_allocation": 0.20
    }
  ]
}
```

**Important**: Total `target_allocation` must sum to 1.0 (100%)

### Running Locally

```bash
# Run analysis
uv run python -m crypto_auto.main

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=crypto_auto --cov-report=html tests/
```

## GitHub Actions Setup

The system runs automatically every Monday at 9 AM UTC via GitHub Actions.

### Setup Steps

1. **Fork this repository** to your GitHub account

2. **Add GitHub Secret**:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `GH_API_TOKEN`
   - Value: Your GitHub Personal Access Token

3. **Enable GitHub Actions**:
   - Go to Actions tab
   - Click "I understand my workflows, go ahead and enable them"

4. **Test Manual Trigger**:
   - Go to Actions → Weekly Portfolio Update
   - Click "Run workflow" → "Run workflow"
   - Check the run completes successfully

5. **Download Results**:
   - After workflow completes, click on the run
   - Scroll to "Artifacts"
   - Download `analysis-results` to view the JSON file

## Output Interpretation

### Console Output

```
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Ticker ┃ Price ($)┃ MCap/FDV┃ Dev Activity ┃ Health  ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ BTC    │ $95,000  │ 97.3%   │ 150          │ ✅ OK   │
│ ETH    │ $4,200   │ 90.9%   │ 200          │ ✅ OK   │
│ SOL    │ $210     │ 35.0%   │ 180          │ ⚠️  FDV │
└────────┴──────────┴─────────┴──────────────┴─────────┘
```

**Health Status**:
- ✅ **OK**: All metrics healthy
- ⚠️ **FDV**: MCap/FDV ratio below warning threshold
- ⚠️ **DEV**: Low developer activity (<10 commits in 30 days)

**Color Coding** (MCap/FDV):
- 🟢 Green: ≥45% (healthy)
- 🟡 Yellow: 40-45% (caution)
- 🔴 Red: <40% (warning - high dilution risk)

### JSON Output

Analysis results are saved to `analysis_YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-01-04T10:00:00Z",
  "projects": [...],
  "rebalance_recommendations": [
    {
      "ticker": "ETH",
      "amount_usd": 600.00,
      "current_price": 4200.00,
      "quantity": 0.14285714
    }
  ],
  "summary": {
    "total_market_cap": 2300000000000,
    "avg_fdv_ratio": 0.677,
    "total_commits": 350,
    "fdv_warnings": 1,
    "low_activity": 0
  }
}
```

## Adding New Projects

1. Find the DeFiLlama slug:
   - Visit [https://defillama.com](https://defillama.com)
   - Search for your project
   - URL will be `https://defillama.com/protocol/PROJECT-SLUG`

2. Find the GitHub repository:
   - Primary development repository (e.g., `solana-labs/solana`)

3. Add to `cryptos.json`:
   ```json
   {
     "ticker": "SOL",
     "name": "Solana",
     "defillama_slug": "solana",
     "github_repos": ["solana-labs/solana"],
     "category": "midcap",
     "target_allocation": 0.10
   }
   ```

4. Adjust other allocations so total = 1.0

## Project Structure

```
crypto-auto/
├── crypto_auto/           # Main application
│   ├── api/              # API clients (DeFiLlama, GitHub)
│   ├── analysis/         # FDV analyzer, rebalancer
│   ├── config/           # Settings, project loader
│   ├── models/           # Data models
│   ├── outputs/          # Console, JSON writers
│   └── main.py           # Entry point
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── .github/workflows/   # GitHub Actions
├── docs/                # Documentation
├── cryptos.json         # Project configuration
└── pyproject.toml       # Dependencies
```

## Development

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/unit/test_fdv_analyzer.py

# With coverage
pytest --cov=crypto_auto tests/

# Verbose output
pytest -vv tests/
```

### Code Quality

```bash
# Run linter
uv run ruff check crypto_auto/

# Auto-fix issues
uv run ruff check --fix crypto_auto/

# Format code
uv run ruff format crypto_auto/

# Pre-commit hooks (if installed)
pre-commit run --all-files
```

## Advanced Features

### Make.com Newsletter Sentiment Analysis

The system can be extended with automated newsletter analysis using Make.com and Gemini AI. See [docs/makecom-integration.md](docs/makecom-integration.md) for setup instructions.

### Custom Rebalancing Logic

The rebalancer implements "rebalancing via additions" to minimize tax events. To customize:

1. Edit `crypto_auto/analysis/rebalancer.py`
2. Modify `calculate_purchase_recommendations()` method
3. Run tests to verify: `pytest tests/unit/test_rebalancer.py`

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | Yes | - | GitHub Personal Access Token |
| `FDV_RATIO_WARNING_THRESHOLD` | No | 0.4 | Warn if MCap/FDV < this value |
| `FDV_RATIO_TARGET_MIN` | No | 0.45 | Target range minimum |
| `FDV_RATIO_TARGET_MAX` | No | 0.50 | Target range maximum |
| `DEV_ACTIVITY_LOOKBACK_DAYS` | No | 30 | Days to analyze for commits |
| `LOG_LEVEL` | No | INFO | Logging level |
| `HTTP_TIMEOUT` | No | 30 | API request timeout (seconds) |
| `MAX_RETRIES` | No | 3 | Max API retry attempts |

### Project Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Cryptocurrency symbol (e.g., "BTC") |
| `name` | string | Yes | Full project name |
| `defillama_slug` | string | Yes | DeFiLlama API identifier |
| `github_repos` | array | Yes | List of repos (format: "owner/repo") |
| `category` | enum | Yes | "core", "midcap", or "experimental" |
| `target_allocation` | float | Yes | Target weight (0.0-1.0) |

## Troubleshooting

### Common Issues

**Problem**: `Configuration file not found: cryptos.json`
- **Solution**: Run from project root directory where `cryptos.json` is located

**Problem**: `GitHub API 401 Unauthorized`
- **Solution**: Check your `GITHUB_TOKEN` in `.env` is valid and not expired

**Problem**: `Total target allocation is 0.XX, but should sum to 1.0`
- **Solution**: Adjust `target_allocation` values in `cryptos.json` to sum to exactly 1.0

**Problem**: Tests fail with `ModuleNotFoundError`
- **Solution**: Run `uv sync` to ensure all dependencies are installed

**Problem**: DeFiLlama returns no data for a project
- **Solution**: Verify the `defillama_slug` is correct by visiting `https://defillama.com/protocol/YOUR-SLUG`

## Security Considerations

- **Never commit `.env` file** - it contains your GitHub token
- **GitHub token permissions**: Only needs read access to public repositories
- **No wallet access**: System is read-only analysis, cannot execute trades
- **No sensitive data**: All market data is public information
- **GitHub Actions secrets**: Secrets are encrypted and never exposed in logs

## Cost Breakdown

| Service | Cost | Limits |
|---------|------|--------|
| GitHub Actions | $0 | 2,000 minutes/month (free tier) |
| DeFiLlama API | $0 | No authentication required |
| GitHub API | $0 | 5,000 requests/hour |
| **Total** | **$0/month** | Weekly runs use ~5 minutes/month |

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is provided as-is for educational and personal use.

## Disclaimer

**This is not financial advice.** This tool is for educational purposes and portfolio tracking only. Always do your own research before making investment decisions. Past performance does not guarantee future results.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/crypto-auto/issues)
- **Documentation**: See `/docs` directory
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/crypto-auto/discussions)

---

Built with Python 3.12+ | uv | DeFiLlama API | GitHub Actions
