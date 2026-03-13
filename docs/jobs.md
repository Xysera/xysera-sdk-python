# Jobs

Every upscale request creates a job record in the Xysera backend. You can retrieve any past job using its `job_id`.

## Retrieving a job

```python
job = client.get_job("550e8400-e29b-41d4-a716-446655440000")
```

The `job_id` is available on the `UpscaleResult` returned by `upscale()`:

```python
result = client.upscale("https://example.com/video.mp4")
job = client.get_job(result.job_id)
```

## Response fields

`get_job()` returns a `JobResult` object:

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | `str` | UUID v4 |
| `status` | `str` | `"complete"` or `"failed"` |
| `model_used` | `str \| None` | Model name used for this job |
| `input_url` | `str \| None` | Original input URL submitted |
| `result_url` | `str \| None` | Pre-signed R2 URL — `None` on failed jobs. Expires 1 hour after job completion. |
| `credits_charged` | `float \| None` | Credits deducted — `None` on failed jobs |
| `processing_time` | `float \| None` | Total wall-clock seconds (`cold_start_time + inference_time`) |
| `cold_start_time` | `float \| None` | Seconds waiting for the worker to wake up — `0` if already warm |
| `inference_time` | `float \| None` | Seconds of actual inference — billing basis |
| `created_at` | `str` | UTC timestamp in ISO 8601 format, e.g. `"2026-03-12T01:44:32+00:00"` |
| `hit_cold_start` | `bool` | `True` if `cold_start_time > 0` — convenience property |

## Handling failed jobs

```python
job = client.get_job(job_id)

if job.status == "failed":
    print("Job failed — no credits were charged.")
elif job.status == "complete":
    print(f"Charged: {job.credits_charged} credits")
    job.download("output.mp4")
```

## Downloading from a job record

`JobResult` has the same `download()` and `adownload()` methods as `UpscaleResult`. Calling `download()` on a failed job (where `result_url` is `None`) raises `ValueError`.

```python
job = client.get_job(job_id)

if job.status == "complete":
    path = job.download("output.mp4")
```

See [Downloading Results](downloading.md) for full details.

## Authorization

A job can only be retrieved by the API key that created it. Requesting a `job_id` that belongs to a different key returns `404` and raises `NotFoundError` — the same as a job that doesn't exist.

## Async

```python
async with xysera.AsyncClient(api_key) as client:
    job = await client.get_job(job_id)
    print(job.status)
```
