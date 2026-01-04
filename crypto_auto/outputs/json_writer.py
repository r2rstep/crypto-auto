import json
from datetime import datetime, timezone
from pathlib import Path
import structlog
from crypto_auto.models.analysis import ProjectAnalysis

logger = structlog.get_logger()


def write_analysis_json(
    projects: list[ProjectAnalysis],
    recommendations: list[dict],
    output_dir: str | Path = ".",
) -> Path:
    timestamp = datetime.now(timezone.utc)
    filename = f"analysis_{timestamp.strftime('%Y-%m-%d')}.json"
    output_path = Path(output_dir) / filename

    data = {
        "timestamp": timestamp.isoformat(),
        "projects": [
            {
                "ticker": p.project.ticker,
                "name": p.project.name,
                "category": p.project.category,
                "market_data": {
                    "price": p.market_data.price,
                    "market_cap": p.market_data.market_cap,
                    "fdv": p.market_data.fdv,
                    "mcap_fdv_ratio": p.market_data.mcap_fdv_ratio,
                },
                "dev_commits_30d": p.dev_commits_30d,
                "health_status": p.health_status,
                "fdv_health": {
                    "status": p.fdv_health.status,
                    "message": p.fdv_health.message,
                    "severity": p.fdv_health.severity,
                    "ratio": p.fdv_health.ratio,
                }
                if p.fdv_health
                else None,
            }
            for p in projects
        ],
        "rebalance_recommendations": recommendations,
        "summary": {
            "total_market_cap": sum(p.market_data.market_cap for p in projects),
            "avg_fdv_ratio": sum(p.market_data.mcap_fdv_ratio for p in projects) / len(projects)
            if projects
            else 0,
            "total_commits": sum(p.dev_commits_30d for p in projects),
            "fdv_warnings": len([p for p in projects if p.health_status == "FDV_WARNING"]),
            "low_activity": len([p for p in projects if p.health_status == "LOW_ACTIVITY"]),
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("analysis_json_written", path=str(output_path), size=output_path.stat().st_size)

    return output_path
