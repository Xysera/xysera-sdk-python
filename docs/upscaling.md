# Upscaling

## Basic usage

```python
result = client.upscale("https://example.com/video.mp4")
```

`upscale()` is **synchronous** — it holds the HTTP connection open until the job completes or fails. The SDK sets a 960-second timeout (16 minutes) automatically. See [how long jobs take](#how-long-jobs-take) below.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_url` | `str` | required | Publicly accessible URL of the input video or image |
| `scale` | `int` | `4` | Upscale factor — `2` or `4` |
| `model` | `str` | `"RealESRGAN_x4plus"` | Model to use — see [models](#models) below |
| `quality` | `str` | `"balanced"` | Quality hint passed to the inference backend |
| `input_duration_seconds` | `float \| None` | `None` | Source video duration in seconds — used for a preflight credit check. See [Credits](credits.md). |

```python
result = client.upscale(
    "https://example.com/video.mp4",
    scale=4,
    model="RealESRGAN_x4plus",
    quality="balanced",
    input_duration_seconds=30.5,
)
```

## Models

| Model | Best for |
|-------|----------|
| `RealESRGAN_x4plus` *(default)* | General video and photos |
| `RealESRGAN_x2plus` | 2× upscaling |
| `realesr-animevideov3` | Anime and animation |

If you request a model that is recognised but not yet deployed, the API returns `503` and the SDK raises `ModelUnavailableError`. If the model name is completely unknown, the SDK raises `ValidationError`.

## Response fields

`upscale()` returns an `UpscaleResult` object:

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `str` | UUID v4 — use with `get_job()` to retrieve this record later |
| `result_url` | `str` | Pre-signed Cloudflare R2 URL. **Expires 1 hour after the job completes.** |
| `width` | `int \| None` | Output width in pixels — `None` if not returned by the inference backend |
| `height` | `int \| None` | Output height in pixels — `None` if not returned by the inference backend |
| `size_bytes` | `int \| None` | Output file size in bytes — `None` if not returned by the inference backend |
| `credits_charged` | `float` | Credits deducted, rounded to 4 decimal places |
| `processing_time` | `float` | Total wall-clock seconds (`cold_start_time + inference_time`) |
| `cold_start_time` | `float` | Seconds spent waiting for the model worker to wake up. `0` if the worker was already warm. **Not billed.** |
| `inference_time` | `float` | Seconds for the actual inference request. This is what billing is based on. |
| `status` | `str` | Always `"complete"` on a successful response |
| `hit_cold_start` | `bool` | `True` if `cold_start_time > 0` — convenience property |

## Cold starts

Xysera runs models on dedicated Hugging Face inference endpoints that scale to zero when idle. If a model hasn't been used recently, the first request in a while will trigger a cold start — the worker needs to boot before inference can begin.

- Cold start wait time is reflected in `cold_start_time` (seconds)
- **Cold start time is not billed** — `credits_charged` is based solely on `inference_time`
- `hit_cold_start` is `True` when `cold_start_time > 0`
- The maximum cold start window is 10 minutes

A job that hits a cold start will show a large `processing_time` but a smaller `credits_charged` than you might expect — this is by design.

```python
result = client.upscale("https://example.com/video.mp4")

if result.hit_cold_start:
    print(f"Cold start: {result.cold_start_time}s (not billed)")

print(f"Inference: {result.inference_time}s")
print(f"Charged:   {result.credits_charged} credits")
```

## How long jobs take

| Scenario | Typical duration |
|----------|-----------------|
| Warm endpoint, short clip | 15–60 seconds |
| Warm endpoint, longer clip | 60–180 seconds |
| Cold start + inference | 2–12 minutes |

The SDK timeout is 960 seconds. If your HTTP client has its own timeout configured, ensure it is at least this high.

## result_url expiry

`result_url` is a pre-signed URL that expires **1 hour** after the job completes. Download the file promptly after receiving a result. If you need to retrieve the URL again, call `get_job(result.job_id)` — but note the URL returned may have already expired if an hour has passed.

See [Downloading Results](downloading.md) for how to save the file to disk.
