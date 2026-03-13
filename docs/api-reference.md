# API Reference

## Client

```python
xysera.Client(api_key, *, base_url="https://api.xysera.com")
```

Synchronous HTTP client. All methods block until a response is received.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `api_key` | `str` | Your Xysera API key (`xys_...`) |
| `base_url` | `str` | Override the API base URL — useful for local development (`http://localhost:8000`) |

---

### `Client.health()`

```python
def health(self) -> dict
```

Check API reachability. No authentication required.

**Returns** `{"status": "ok"}` when the API is up.

**Timeout:** 30 seconds.

---

### `Client.upscale()`

```python
def upscale(
    self,
    input_url: str,
    *,
    scale: int = 4,
    model: str = "RealESRGAN_x4plus",
    quality: str = "balanced",
    input_duration_seconds: float | None = None,
) -> UpscaleResult
```

Submit a video or image for upscaling. Blocks until the job completes.

**Parameters**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `input_url` | `str` | required | Publicly accessible URL of the source file |
| `scale` | `int` | `4` | Upscale factor — `2` or `4` |
| `model` | `str` | `"RealESRGAN_x4plus"` | Inference model — see [models](upscaling.md#models) |
| `quality` | `str` | `"balanced"` | Quality hint forwarded to the inference backend |
| `input_duration_seconds` | `float \| None` | `None` | Source duration in seconds — enables a preflight credit check |

**Returns** `UpscaleResult`

**Raises** `AuthenticationError`, `InsufficientCreditsError`, `ValidationError`, `RateLimitError`, `JobFailedError`, `ModelUnavailableError`

**Timeout:** 960 seconds.

---

### `Client.get_credits()`

```python
def get_credits(self) -> CreditsResult
```

Return the credit balance and label for the authenticated key.

**Returns** `CreditsResult`

**Raises** `AuthenticationError`

**Timeout:** 30 seconds.

---

### `Client.get_job()`

```python
def get_job(self, job_id: str) -> JobResult
```

Retrieve a job record by ID. The authenticated key must own the job.

**Parameters**

| Name | Type | Description |
|------|------|-------------|
| `job_id` | `str` | UUID v4 returned by `upscale()` |

**Returns** `JobResult`

**Raises** `AuthenticationError`, `NotFoundError`

**Timeout:** 30 seconds.

---

## AsyncClient

```python
xysera.AsyncClient(api_key, *, base_url="https://api.xysera.com")
```

Asynchronous HTTP client. All methods are coroutines and must be awaited. Identical interface to `Client`.

Supports use as an async context manager for connection reuse:

```python
async with xysera.AsyncClient(api_key) as client:
    result = await client.upscale("https://example.com/video.mp4")
```

**Methods:** `health()`, `upscale()`, `get_credits()`, `get_job()` — same signatures as `Client`, all `async`.

---

## UpscaleResult

Returned by `Client.upscale()` and `AsyncClient.upscale()`.

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `str` | UUID v4 job identifier |
| `result_url` | `str` | Pre-signed R2 URL — expires 1 hour after job completion |
| `width` | `int \| None` | Output width in pixels |
| `height` | `int \| None` | Output height in pixels |
| `size_bytes` | `int \| None` | Output file size in bytes |
| `credits_charged` | `float` | Credits deducted, rounded to 4dp |
| `processing_time` | `float` | Total seconds (`cold_start_time + inference_time`) |
| `cold_start_time` | `float` | Seconds waiting for the worker to boot — `0` if warm. Not billed. |
| `inference_time` | `float` | Seconds of actual inference — billing basis |
| `status` | `str` | Always `"complete"` |
| `hit_cold_start` | `bool` | `True` if `cold_start_time > 0` |

### `UpscaleResult.download()`

```python
def download(self, dest: str | Path) -> Path
```

Download the result file to `dest`. Pass a file path or a directory (filename inferred from URL). Returns the resolved absolute path.

**Timeout:** 300 seconds.

### `UpscaleResult.adownload()`

```python
async def adownload(self, dest: str | Path) -> Path
```

Async version of `download()`.

---

## JobResult

Returned by `Client.get_job()` and `AsyncClient.get_job()`.

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `str` | UUID v4 |
| `status` | `str` | `"complete"` or `"failed"` |
| `model_used` | `str \| None` | Model used for this job |
| `input_url` | `str \| None` | Original input URL |
| `result_url` | `str \| None` | Pre-signed R2 URL — `None` on failed jobs |
| `credits_charged` | `float \| None` | Credits deducted — `None` on failed jobs |
| `processing_time` | `float \| None` | Total seconds — `None` on very old jobs |
| `cold_start_time` | `float \| None` | Cold start seconds — `None` on very old jobs |
| `inference_time` | `float \| None` | Inference seconds — `None` on very old jobs |
| `created_at` | `str` | UTC timestamp (ISO 8601), e.g. `"2026-03-12T01:44:32+00:00"` |
| `hit_cold_start` | `bool` | `True` if `cold_start_time > 0` |

### `JobResult.download()`

```python
def download(self, dest: str | Path) -> Path
```

Download the result file. Raises `ValueError` if the job has no `result_url` (i.e. it failed).

### `JobResult.adownload()`

```python
async def adownload(self, dest: str | Path) -> Path
```

Async version of `download()`.

---

## CreditsResult

Returned by `Client.get_credits()` and `AsyncClient.get_credits()`.

| Field | Type | Description |
|-------|------|-------------|
| `credits_balance` | `float` | Current balance, rounded to 4dp |
| `key_label` | `str \| None` | Human-readable label set at key creation |

---

## Exceptions

All exceptions inherit from `xysera.XyseraError` and expose `status_code: int`.

| Exception | HTTP status | Raised by |
|-----------|-------------|-----------|
| `XyseraError` | any | base class |
| `AuthenticationError` | 401, 403 | all methods |
| `InsufficientCreditsError` | 402 | `upscale()` |
| `ValidationError` | 422 | `upscale()` |
| `RateLimitError` | 429 | all methods |
| `NotFoundError` | 404 | `get_job()` |
| `JobFailedError` | 502 | `upscale()` |
| `ModelUnavailableError` | 503 | `upscale()` |

See [Error Handling](error-handling.md) for usage examples.
