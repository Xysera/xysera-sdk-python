# Error Handling

All SDK exceptions inherit from `xysera.XyseraError`, which itself inherits from `Exception`. Every exception exposes a `status_code` attribute containing the HTTP status code returned by the API.

## Exception hierarchy

```
XyseraError                 base — all errors
├── AuthenticationError     401 / 403  invalid or missing API key
├── InsufficientCreditsError  402      not enough credits
├── ValidationError           422      invalid request parameters
├── RateLimitError            429      too many requests
├── NotFoundError             404      job not found or belongs to a different key
├── JobFailedError            502      inference backend failed — no charge
└── ModelUnavailableError     503      model recognised but not yet deployed
```

## Recommended pattern

Catch specific exceptions first, then fall back to the base class for anything unexpected:

```python
import xysera

client = xysera.Client(api_key)

try:
    result = client.upscale("https://example.com/video.mp4")
except xysera.AuthenticationError:
    # Invalid or missing API key (HTTP 401 or 403)
    print("Check your API key.")
except xysera.InsufficientCreditsError:
    # Balance too low — the job was never started
    print("Top up your credits at xysera.com.")
except xysera.ValidationError as e:
    # Bad parameters — e.g. unknown model name
    print(f"Invalid request: {e}")
except xysera.RateLimitError:
    # Exceeded 5 req/min on /upscale
    print("Rate limit hit — wait before retrying.")
except xysera.JobFailedError:
    # Inference backend returned an error — no credits charged
    print("Processing failed. No credits were deducted.")
except xysera.ModelUnavailableError:
    # Recognised model, not yet deployed
    print("This model is not yet available. Try RealESRGAN_x4plus.")
except xysera.NotFoundError:
    # Only raised by get_job() — job doesn't exist or wrong key
    print("Job not found.")
except xysera.XyseraError as e:
    # Catch-all for any other API error
    print(f"API error (HTTP {e.status_code}): {e}")
```

## Exception reference

### `AuthenticationError` — HTTP 401 / 403

Raised when:
- The `Authorization` header is missing (403)
- The API key is not recognised (401)

Both map to the same exception. If you see this, verify your key is correct and the `XYSERA_API_KEY` environment variable is set.

### `InsufficientCreditsError` — HTTP 402

Raised before a job starts if your credit balance is insufficient. No inference was attempted and no credits were charged.

If you provide `input_duration_seconds`, the API estimates `(duration / 60) * 2` credits required. Without it, the check falls back to `balance > 0`. See [Credits](credits.md).

### `ValidationError` — HTTP 422

Raised when request parameters are invalid — most commonly when `model` is a completely unknown string. Check the [available models](upscaling.md#models).

### `RateLimitError` — HTTP 429

Raised when you exceed the per-key rate limit:

| Endpoint | Limit |
|----------|-------|
| `POST /upscale` | 5 requests / minute |
| `GET /credits` | 60 requests / minute |
| `GET /jobs/{job_id}` | 60 requests / minute |

Back off and retry after a minute. When running concurrent async jobs, use a semaphore to stay within limits.

### `NotFoundError` — HTTP 404

Raised by `get_job()` when the job ID does not exist or was created by a different API key. The API intentionally returns 404 (not 403) in both cases.

### `JobFailedError` — HTTP 502

Raised when the inference backend returned a non-200 response after all retries. The job is saved as `status = "failed"` in the backend. **No credits are charged.**

This is typically a transient backend error — retrying the same request usually succeeds.

### `ModelUnavailableError` — HTTP 503

Raised when the requested model is in the recognised list but not yet deployed. Currently affects `BasicVSR` and `CodeFormer`. Use `RealESRGAN_x4plus`, `RealESRGAN_x2plus`, or `realesr-animevideov3` instead.

### `XyseraError` — base class

All exceptions above inherit from `XyseraError`. Use it as a catch-all:

```python
except xysera.XyseraError as e:
    print(e.status_code)  # HTTP status code
    print(str(e))         # human-readable message from the API
```
