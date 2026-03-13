# Downloading Results

After a successful `upscale()` call, the result can be saved to disk using the `.download()` method on the result object. This is a convenience wrapper around the pre-signed `result_url`.

## Sync download

```python
result = client.upscale("https://example.com/video.mp4")

# Pass a file path
path = result.download("output.mp4")
print(path)  # /absolute/path/to/output.mp4

# Or pass a directory — filename is inferred from the URL
path = result.download("/tmp/xysera-outputs/")
```

`download()` returns the resolved absolute `Path` of the saved file.

## Async download

```python
async with xysera.AsyncClient(api_key) as client:
    result = await client.upscale("https://example.com/video.mp4")
    path = await result.adownload("output.mp4")
```

Use `adownload()` inside async contexts. Do not call the sync `download()` from an async function — it will block the event loop.

## Downloading a past job

`JobResult` (returned by `get_job()`) has the same `download()` and `adownload()` methods:

```python
job = client.get_job("550e8400-e29b-41d4-a716-446655440000")

if job.status == "complete":
    job.download("output.mp4")
```

Calling `download()` on a failed job (where `result_url` is `None`) raises `ValueError`.

## result_url expiry

The `result_url` underlying these downloads is a pre-signed Cloudflare R2 URL that **expires 1 hour after the job completes**. If you call `download()` more than an hour after upscaling, the request will fail with an HTTP error from the storage backend.

Download files promptly after receiving a result.

## Download timeout

The SDK uses a 300-second (5-minute) timeout for download requests. Large output files on slow connections may require retrying if the download times out.
