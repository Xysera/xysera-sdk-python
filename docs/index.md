# Xysera Python SDK

The official Python SDK for the [Xysera API](https://xysera.com) — AI-powered video and image upscaling.

## Requirements

- Python 3.10+
- An Xysera API key ([xysera.com](https://xysera.com))

## Installation

```bash
pip install xysera
```

## Documentation

| Page | Description |
|------|-------------|
| [Quickstart](quickstart.md) | Install and run your first upscale in minutes |
| [Authentication](authentication.md) | API keys and how auth works |
| [Upscaling](upscaling.md) | Models, parameters, and response fields |
| [Downloading Results](downloading.md) | Save upscaled files to disk |
| [Credits](credits.md) | How billing and the credit system works |
| [Jobs](jobs.md) | Retrieving past job records |
| [Async Usage](async.md) | Using `AsyncClient` with `asyncio` |
| [Error Handling](error-handling.md) | All exceptions and how to handle them |
| [API Reference](api-reference.md) | Complete SDK reference |

## At a glance

```python
import xysera

client = xysera.Client("xys_...")
result = client.upscale("https://example.com/video.mp4")

print(result.result_url)       # pre-signed URL — valid for 1 hour
print(result.credits_charged)  # credits deducted for this job
result.download("output.mp4")  # save to disk
```
