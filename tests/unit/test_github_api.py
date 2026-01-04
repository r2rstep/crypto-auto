import pytest
import respx
import httpx
from crypto_auto.api.github_api import GitHubClient
from crypto_auto.config.settings import settings


@pytest.mark.asyncio
async def test_github_get_commit_activity_success(respx_mock):
    mock_commits = [
        {"sha": "abc123", "commit": {"message": "Fix bug"}},
        {"sha": "def456", "commit": {"message": "Add feature"}},
        {"sha": "ghi789", "commit": {"message": "Update docs"}},
    ]

    respx_mock.get("https://api.github.com/repos/bitcoin/bitcoin/commits").mock(
        return_value=httpx.Response(200, json=mock_commits)
    )

    async with GitHubClient() as client:
        commit_count = await client.get_commit_activity("bitcoin/bitcoin", days=30)

    assert commit_count == 3


@pytest.mark.asyncio
async def test_github_get_commit_activity_empty(respx_mock):
    respx_mock.get("https://api.github.com/repos/test/test/commits").mock(
        return_value=httpx.Response(200, json=[])
    )

    async with GitHubClient() as client:
        commit_count = await client.get_commit_activity("test/test", days=30)

    assert commit_count == 0


@pytest.mark.asyncio
async def test_github_get_commit_activity_pagination_warning(respx_mock):
    mock_commits = [{"sha": f"sha{i}", "commit": {"message": f"Commit {i}"}} for i in range(100)]

    respx_mock.get("https://api.github.com/repos/active/repo/commits").mock(
        return_value=httpx.Response(200, json=mock_commits)
    )

    async with GitHubClient() as client:
        commit_count = await client.get_commit_activity("active/repo", days=30)

    assert commit_count == 100


@pytest.mark.asyncio
async def test_github_authorization_header(respx_mock):
    route = respx_mock.get("https://api.github.com/repos/test/repo/commits").mock(
        return_value=httpx.Response(200, json=[])
    )

    async with GitHubClient() as client:
        await client.get_commit_activity("test/repo")

    assert route.called
    assert route.calls.last.request.headers["Authorization"] == f"token {settings.github_token}"


@pytest.mark.asyncio
async def test_github_api_error_returns_zero(respx_mock):
    respx_mock.get("https://api.github.com/repos/error/repo/commits").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    async with GitHubClient() as client:
        commit_count = await client.get_commit_activity("error/repo")

    assert commit_count == 0


@pytest.mark.asyncio
async def test_github_unexpected_response_type(respx_mock):
    respx_mock.get("https://api.github.com/repos/test/repo/commits").mock(
        return_value=httpx.Response(200, json={"unexpected": "format"})
    )

    async with GitHubClient() as client:
        commit_count = await client.get_commit_activity("test/repo")

    assert commit_count == 0


@pytest.mark.asyncio
async def test_github_since_parameter(respx_mock):
    route = respx_mock.get("https://api.github.com/repos/test/repo/commits").mock(
        return_value=httpx.Response(200, json=[])
    )

    async with GitHubClient() as client:
        await client.get_commit_activity("test/repo", days=30)

    assert route.called
    request = route.calls.last.request
    assert "since" in str(request.url)
    assert "per_page=100" in str(request.url)
