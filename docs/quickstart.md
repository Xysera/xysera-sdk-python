# Quickstart

## 1. Install

```bash
pip install xysera
```

## 2. Get an API key

Log in at [xysera.com](https://xysera.com) and create an API key. Keys have the format `xys_` followed by 32 alphanumeric characters.

Store it as an environment variable — never hardcode it in your source:

```bash
export XYSERA_API_KEY="xys_..."
```

## 3. Upscale a video

```python
import os
import xysera

client = xysera.Client(os.environ["XYSERA_API_KEY"])

result = client.upscale("https://example.com/video.mp4")

print(result.result_url)       # pre-signed download URL (valid 1 hour)
print(result.credits_charged)  # credits deducted
result.download("output.mp4")  # save to disk
```

> **Note:** `upscale()` is synchronous — it holds the connection open until the job finishes. Processing typically takes 20–180 seconds depending on file length and whether the model was warm. See [Upscaling](upscaling.md) for details.

## 4. Check your balance

```python
credits = client.get_credits()
print(credits.credits_balance)  # e.g. 42.5
```

## 5. Async usage

If you're in an `asyncio` application, use `AsyncClient` instead:

```python
import asyncio
import os
import xysera

async def main():
    async with xysera.AsyncClient(os.environ["XYSERA_API_KEY"]) as client:
        result = await client.upscale("https://example.com/video.mp4")
        await result.adownload("output.mp4")

asyncio.run(main())
```

## Next steps

- [Upscaling](upscaling.md) — models, scale factors, and all response fields
- [Error Handling](error-handling.md) — handle auth errors, insufficient credits, and more
- [Credits](credits.md) — understand how billing works
