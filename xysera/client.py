from __future__ import annotations

import httpx

from .exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    JobFailedError,
    ModelUnavailableError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    XyseraError,
)
from .models import CreditsResult, JobResult, UpscaleResult

_BASE_URL = "https://api.xysera.com"
_UPSCALE_TIMEOUT = 960.0
_DEFAULT_TIMEOUT = 30.0


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        detail = response.json().get("detail", response.text)
    except Exception:
        detail = response.text

    status = response.status_code
    if status in (401, 403):
        raise AuthenticationError(detail, status_code=status)
    if status == 402:
        raise InsufficientCreditsError(detail, status_code=status)
    if status == 422:
        raise ValidationError(detail, status_code=status)
    if status == 429:
        raise RateLimitError(detail, status_code=status)
    if status == 404:
        raise NotFoundError(detail, status_code=status)
    if status == 502:
        raise JobFailedError(detail, status_code=status)
    if status == 503:
        raise ModelUnavailableError(detail, status_code=status)
    raise XyseraError(detail, status_code=status)


def _upscale_result_from_dict(data: dict) -> UpscaleResult:
    return UpscaleResult(
        job_id=data["job_id"],
        result_url=data["result_url"],
        width=data.get("width"),
        height=data.get("height"),
        size_bytes=data.get("size_bytes"),
        credits_charged=data["credits_charged"],
        processing_time=data["processing_time"],
        cold_start_time=data["cold_start_time"],
        inference_time=data["inference_time"],
        status=data["status"],
    )


def _job_result_from_dict(data: dict) -> JobResult:
    return JobResult(
        job_id=data["job_id"],
        status=data["status"],
        model_used=data.get("model_used"),
        input_url=data.get("input_url"),
        result_url=data.get("result_url"),
        credits_charged=data.get("credits_charged"),
        processing_time=data.get("processing_time"),
        cold_start_time=data.get("cold_start_time"),
        inference_time=data.get("inference_time"),
        created_at=data["created_at"],
    )


class Client:
    """Synchronous Xysera API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}

    def health(self) -> dict:
        """Check API health. Returns ``{"status": "ok"}`` when the API is reachable."""
        with httpx.Client(timeout=_DEFAULT_TIMEOUT) as http:
            response = http.get(f"{self._base_url}/health")
        _raise_for_status(response)
        return response.json()

    def upscale(
        self,
        input_url: str,
        *,
        scale: int = 4,
        model: str = "RealESRGAN_x4plus",
        quality: str = "balanced",
        input_duration_seconds: float | None = None,
    ) -> UpscaleResult:
        """Upscale a video or image. Blocks until the job completes (up to 960 s)."""
        body: dict = {
            "input_url": input_url,
            "scale": scale,
            "model": model,
            "quality": quality,
        }
        if input_duration_seconds is not None:
            body["input_duration_seconds"] = input_duration_seconds

        with httpx.Client(timeout=_UPSCALE_TIMEOUT) as http:
            response = http.post(
                f"{self._base_url}/upscale",
                json=body,
                headers=self._headers,
            )
        _raise_for_status(response)
        return _upscale_result_from_dict(response.json())

    def get_credits(self) -> CreditsResult:
        """Return the current credits balance and key label for this API key."""
        with httpx.Client(timeout=_DEFAULT_TIMEOUT) as http:
            response = http.get(
                f"{self._base_url}/credits",
                headers=self._headers,
            )
        _raise_for_status(response)
        data = response.json()
        return CreditsResult(
            credits_balance=data["credits_balance"],
            key_label=data.get("key_label"),
        )

    def get_job(self, job_id: str) -> JobResult:
        """Retrieve a job record by ID."""
        with httpx.Client(timeout=_DEFAULT_TIMEOUT) as http:
            response = http.get(
                f"{self._base_url}/jobs/{job_id}",
                headers=self._headers,
            )
        _raise_for_status(response)
        return _job_result_from_dict(response.json())


class AsyncClient:
    """Asynchronous Xysera API client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._http: httpx.AsyncClient | None = None

    async def __aenter__(self) -> AsyncClient:
        self._http = httpx.AsyncClient()
        return self

    async def __aexit__(self, *_) -> None:
        if self._http is not None:
            await self._http.aclose()
            self._http = None

    def _client(self, timeout: float) -> httpx.AsyncClient:
        if self._http is not None:
            # Reuse the managed client but honour the per-request timeout.
            self._http.timeout = httpx.Timeout(timeout)
            return self._http
        # Standalone (non-context-manager) usage — caller must close.
        return httpx.AsyncClient(timeout=timeout)

    async def health(self) -> dict:
        """Check API health. Returns ``{"status": "ok"}`` when the API is reachable."""
        client = self._client(_DEFAULT_TIMEOUT)
        owned = self._http is None
        try:
            response = await client.get(f"{self._base_url}/health")
        finally:
            if owned:
                await client.aclose()
        _raise_for_status(response)
        return response.json()

    async def upscale(
        self,
        input_url: str,
        *,
        scale: int = 4,
        model: str = "RealESRGAN_x4plus",
        quality: str = "balanced",
        input_duration_seconds: float | None = None,
    ) -> UpscaleResult:
        """Upscale a video or image. Awaits until the job completes (up to 960 s)."""
        body: dict = {
            "input_url": input_url,
            "scale": scale,
            "model": model,
            "quality": quality,
        }
        if input_duration_seconds is not None:
            body["input_duration_seconds"] = input_duration_seconds

        client = self._client(_UPSCALE_TIMEOUT)
        owned = self._http is None
        try:
            response = await client.post(
                f"{self._base_url}/upscale",
                json=body,
                headers=self._headers,
            )
        finally:
            if owned:
                await client.aclose()
        _raise_for_status(response)
        return _upscale_result_from_dict(response.json())

    async def get_credits(self) -> CreditsResult:
        """Return the current credits balance and key label for this API key."""
        client = self._client(_DEFAULT_TIMEOUT)
        owned = self._http is None
        try:
            response = await client.get(
                f"{self._base_url}/credits",
                headers=self._headers,
            )
        finally:
            if owned:
                await client.aclose()
        _raise_for_status(response)
        data = response.json()
        return CreditsResult(
            credits_balance=data["credits_balance"],
            key_label=data.get("key_label"),
        )

    async def get_job(self, job_id: str) -> JobResult:
        """Retrieve a job record by ID."""
        client = self._client(_DEFAULT_TIMEOUT)
        owned = self._http is None
        try:
            response = await client.get(
                f"{self._base_url}/jobs/{job_id}",
                headers=self._headers,
            )
        finally:
            if owned:
                await client.aclose()
        _raise_for_status(response)
        return _job_result_from_dict(response.json())
