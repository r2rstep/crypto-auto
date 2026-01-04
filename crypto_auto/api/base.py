import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from crypto_auto.config.settings import settings

logger = structlog.get_logger()


class APIError(Exception):
    pass


class BaseAPIClient:
    def __init__(self, base_url: str, headers: dict | None = None):
        self.base_url = base_url
        self.headers = headers or {}
        self.client = httpx.AsyncClient(
            timeout=settings.http_timeout,
            headers=self.headers,
        )

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        logger.info("api_request", method="GET", url=url, params=params)

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info("api_response", status=response.status_code, url=url)
            return data
        except httpx.HTTPStatusError as e:
            logger.error(
                "api_http_error",
                status=e.response.status_code,
                url=url,
                response_text=e.response.text[:200],
            )
            raise APIError(f"HTTP {e.response.status_code}: {url}") from e
        except httpx.TimeoutException as e:
            logger.error("api_timeout", url=url)
            raise
        except httpx.RequestError as e:
            logger.error("api_request_error", error=str(e), url=url)
            raise APIError(f"Request failed: {url}") from e
        except ValueError as e:
            logger.error("api_json_decode_error", error=str(e), url=url)
            raise APIError(f"Invalid JSON response from {url}") from e

    async def close(self):
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
