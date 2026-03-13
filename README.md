# xysera

[![PyPI version](https://img.shields.io/pypi/v/xysera?color=blue)](https://pypi.org/project/xysera/)
[![Python versions](https://img.shields.io/pypi/pyversions/xysera)](https://pypi.org/project/xysera/)
[![CI](https://img.shields.io/github/actions/workflow/status/Xysera/xysera-sdk-python/ci.yml?branch=main&label=CI)](https://github.com/Xysera/xysera-sdk-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Official Python SDK for the [Xysera](https://xysera.com) API.

## Installation

```bash
pip install xysera
```

Requires Python 3.10+ and installs [httpx](https://www.python-httpx.org/) automatically.

## Quick start

```python
import xysera

client = xysera.Client("xys_your_api_key_here")
result = client.upscale("https://example.com/video.mp4")
print(result.result_url)       # download before it expires (1 hour)
print(result.credits_charged)  # credits deducted for this job
```

---

## Endpoints

### Upscale a video or image

```python
result = client.upscale(
    "https://example.com/video.mp4",
    scale=4,                            # 2 or 4 (default 4)
    model="RealESRGAN_x4plus",          # see models below
    quality="balanced",
    input_duration_seconds=120.5,       # optional — used for preflight credit estimate
)

print(result.job_id)
print(result.result_url)        # pre-signed URL, valid for 1 hour
print(result.width)
print(result.height)
print(result.size_bytes)
print(result.credits_charged)
print(result.processing_time)
print(result.cold_start_time)
print(result.inference_time)
print(result.status)            # "complete"
print(result.hit_cold_start)    # True if the worker cold-started (cold_start_time > 0)
```

**Available models**

| Model | Best for |
|---|---|
| `RealESRGAN_x4plus` *(default)* | General photos and video |
| `RealESRGAN_x2plus` | 2× upscaling |
| `realesr-animevideov3` | Anime / animation |

> **Note:** `result_url` is a pre-signed download URL that expires **1 hour** after the job completes. Download the file promptly — calling `get_job` later will return the same URL, but it may have expired.

> **Cold starts:** When a model worker hasn't been used recently it may need to cold-start before your job runs. `result.hit_cold_start` is `True` when this happened. Cold starts are reflected in `cold_start_time` (seconds) and are included in `processing_time`.

The upscale endpoint is **synchronous** — it holds the connection open until the job completes (up to 16 minutes). The SDK sets a 960-second timeout automatically.

---

### Check credits

```python
credits = client.get_credits()
print(credits.credits_balance)  # float
print(credits.key_label)        # str | None — human-readable label for the key
```

---

### Retrieve a job

```python
job = client.get_job("job_abc123")
print(job.job_id)
print(job.status)           # "complete" or "failed"
print(job.result_url)       # None if failed
print(job.credits_charged)  # None if failed
```

---

## Async usage

```python
import asyncio
import xysera

async def main():
    async with xysera.AsyncClient("xys_your_api_key_here") as client:
        result = await client.upscale("https://example.com/video.mp4", scale=4)
        print(result.result_url)

        credits = await client.get_credits()
        print(credits.credits_balance)

        job = await client.get_job(result.job_id)
        print(job.status)

asyncio.run(main())
```

---

## Error handling

```python
import xysera

client = xysera.Client("xys_your_api_key_here")

try:
    result = client.upscale("https://example.com/video.mp4")
except xysera.AuthenticationError:
    print("Invalid or missing API key.")
except xysera.InsufficientCreditsError:
    print("Not enough credits — top up your account.")
except xysera.ValidationError as e:
    print(f"Bad request: {e}")
except xysera.RateLimitError:
    print("Rate limit hit — slow down requests.")
except xysera.JobFailedError:
    print("Processing failed on the server. No credits were charged.")
except xysera.ModelUnavailableError:
    print("The requested model is not yet deployed.")
except xysera.XyseraError as e:
    print(f"Unexpected API error (HTTP {e.status_code}): {e}")
```

All exceptions inherit from `xysera.XyseraError` and expose a `status_code` attribute with the HTTP status code returned by the API.

| Exception | HTTP status | Description |
|---|---|---|
| `AuthenticationError` | 401 | Invalid or missing API key |
| `InsufficientCreditsError` | 402 | Account has insufficient credits |
| `ValidationError` | 422 | Invalid request parameters |
| `RateLimitError` | 429 | Too many requests |
| `JobFailedError` | 502 | Upstream processing failed; no credits charged |
| `ModelUnavailableError` | 503 | Model not yet deployed |

---

## Rate limits

| Endpoint | Limit |
|---|---|
| `POST /upscale` | 5 req / min |
| `GET /credits` | 60 req / min |
| `GET /jobs/{job_id}` | 60 req / min |
