from datetime import datetime, timedelta, timezone
import structlog
from crypto_auto.api.base import BaseAPIClient
from crypto_auto.config.settings import settings

logger = structlog.get_logger()


class GitHubClient(BaseAPIClient):
    def __init__(self):
        super().__init__(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"token {settings.github_token}",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    async def get_commit_activity(self, repo: str, days: int = 30) -> int:
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        endpoint = f"/repos/{repo}/commits"
        params = {"since": since, "per_page": 100}

        try:
            commits = await self.get(endpoint, params=params)

            if not isinstance(commits, list):
                logger.error("unexpected_response_type", repo=repo, response_type=type(commits))
                return 0

            commit_count = len(commits)

            if commit_count >= 100:
                logger.warning(
                    "max_commits_reached",
                    repo=repo,
                    commits=commit_count,
                    message="May be more commits than returned (pagination not implemented)",
                )

            logger.info("github_activity_fetched", repo=repo, commits=commit_count, days=days)
            return commit_count

        except Exception as e:
            logger.error("github_activity_fetch_failed", repo=repo, error=str(e))
            return 0
