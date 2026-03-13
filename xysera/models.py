from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class UpscaleResult:
    job_id: str
    result_url: str
    width: int
    height: int
    size_bytes: int
    credits_charged: float
    processing_time: float
    cold_start_time: float
    inference_time: float
    status: str

    @property
    def hit_cold_start(self) -> bool:
        """True if the worker had to cold-start before processing this job."""
        return self.cold_start_time > 0

    def download(self, dest: str | Path) -> Path:
        """Download the result file to *dest* and return the resolved path.

        *dest* may be a directory (file is saved inside it using the filename
        from the URL) or a full file path.
        """
        import httpx

        dest = Path(dest)
        if dest.is_dir():
            filename = self.result_url.split("?")[0].rsplit("/", 1)[-1]
            dest = dest / filename

        with httpx.Client(timeout=300) as http:
            with http.stream("GET", self.result_url) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                        f.write(chunk)

        return dest.resolve()

    async def adownload(self, dest: str | Path) -> Path:
        """Async version of :meth:`download`."""
        import httpx

        dest = Path(dest)
        if dest.is_dir():
            filename = self.result_url.split("?")[0].rsplit("/", 1)[-1]
            dest = dest / filename

        async with httpx.AsyncClient(timeout=300) as http:
            async with http.stream("GET", self.result_url) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        f.write(chunk)

        return dest.resolve()


@dataclass
class JobResult:
    job_id: str
    status: str
    result_url: str | None
    credits_charged: float | None
    processing_time: float | None
    cold_start_time: float | None
    inference_time: float | None

    @property
    def hit_cold_start(self) -> bool:
        """True if the worker had to cold-start before processing this job."""
        return (self.cold_start_time or 0) > 0

    def download(self, dest: str | Path) -> Path:
        """Download the result file to *dest*. Raises ValueError if job failed."""
        if not self.result_url:
            raise ValueError(f"Job {self.job_id} has no result_url (status={self.status})")

        import httpx

        dest = Path(dest)
        if dest.is_dir():
            filename = self.result_url.split("?")[0].rsplit("/", 1)[-1]
            dest = dest / filename

        with httpx.Client(timeout=300) as http:
            with http.stream("GET", self.result_url) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                        f.write(chunk)

        return dest.resolve()

    async def adownload(self, dest: str | Path) -> Path:
        """Async version of :meth:`download`."""
        if not self.result_url:
            raise ValueError(f"Job {self.job_id} has no result_url (status={self.status})")

        import httpx

        dest = Path(dest)
        if dest.is_dir():
            filename = self.result_url.split("?")[0].rsplit("/", 1)[-1]
            dest = dest / filename

        async with httpx.AsyncClient(timeout=300) as http:
            async with http.stream("GET", self.result_url) as response:
                response.raise_for_status()
                with open(dest, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=1024 * 1024):
                        f.write(chunk)

        return dest.resolve()


@dataclass
class CreditsResult:
    credits_balance: float
    key_label: str | None
