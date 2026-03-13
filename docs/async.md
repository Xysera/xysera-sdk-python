# Async Usage

The SDK provides `AsyncClient` for use in `asyncio` applications. It has the same methods as `Client` but all are `async` and must be awaited.

## Basic usage

```python
import asyncio
import os
import xysera

async def main():
    async with xysera.AsyncClient(os.environ["XYSERA_API_KEY"]) as client:
        result = await client.upscale("https://example.com/video.mp4")
        print(result.result_url)
        await result.adownload("output.mp4")

asyncio.run(main())
```

## Context manager

Using `AsyncClient` as an async context manager (`async with`) is recommended when making more than one request. It creates a single persistent HTTP connection that is reused across all calls, then cleanly closed on exit.

```python
async with xysera.AsyncClient(api_key) as client:
    credits = await client.get_credits()
    result  = await client.upscale("https://example.com/video.mp4")
    job     = await client.get_job(result.job_id)
```

## Without a context manager

For one-off calls, the context manager is optional — the client creates and closes an HTTP connection per request:

```python
client = xysera.AsyncClient(api_key)
credits = await client.get_credits()
```

## Running concurrent jobs

`AsyncClient` is well-suited for running multiple upscale jobs concurrently:

```python
import asyncio
import xysera

async def upscale_all(api_key: str, urls: list[str]) -> list[xysera.UpscaleResult]:
    async with xysera.AsyncClient(api_key) as client:
        tasks = [client.upscale(url) for url in urls]
        return await asyncio.gather(*tasks)

results = asyncio.run(upscale_all(api_key, [
    "https://example.com/clip1.mp4",
    "https://example.com/clip2.mp4",
]))
```

> **Rate limit:** `POST /upscale` is limited to **5 requests per minute** per API key. `asyncio.gather` will fire all requests simultaneously — if you exceed 5, some will raise `RateLimitError`. Use `asyncio.Semaphore` or batch your requests if you have more than 5 URLs.

## Downloading async

Use `adownload()` inside async contexts — the sync `download()` blocks the event loop:

```python
result = await client.upscale("https://example.com/video.mp4")
path = await result.adownload("output.mp4")  # correct
path = result.download("output.mp4")          # blocks the event loop — avoid
```

## Framework integration

### FastAPI

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import xysera

xysera_client: xysera.AsyncClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    global xysera_client
    xysera_client = xysera.AsyncClient(os.environ["XYSERA_API_KEY"])
    yield
    await xysera_client._http.aclose() if xysera_client._http else None

app = FastAPI(lifespan=lifespan)

@app.post("/upscale")
async def upscale(url: str):
    result = await xysera_client.upscale(url)
    return {"result_url": result.result_url}
```

### Django (async views)

```python
import xysera

async def upscale_view(request):
    client = xysera.AsyncClient(os.environ["XYSERA_API_KEY"])
    result = await client.upscale(request.POST["url"])
    return JsonResponse({"result_url": result.result_url})
```
