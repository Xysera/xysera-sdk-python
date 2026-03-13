# Credits

## How credits work

Xysera uses a credit-based billing model:

- **1 credit = 1 minute of inference time**
- **1 credit = $0.10**

Credits are deducted automatically when a job completes. Failed jobs are never charged.

## Checking your balance

```python
credits = client.get_credits()
print(credits.credits_balance)  # e.g. 42.5
print(credits.key_label)        # e.g. "prod" — label set at key creation, or None
```

## How charges are calculated

Billing is based on **inference time only** — the time spent running the AI model. Cold start wait time is explicitly excluded.

```
credits_charged = round(inference_time_seconds / 60.0, 4)
```

The charge is rounded to 4 decimal places with no minimum — you pay exactly for what you use.

```python
result = client.upscale("https://example.com/video.mp4")

print(f"Inference time:  {result.inference_time}s")
print(f"Cold start time: {result.cold_start_time}s  ← not billed")
print(f"Credits charged: {result.credits_charged}")
```

## Preflight credit check

Before sending a job to the inference backend, the API estimates whether you have enough credits:

```
estimated_credits = (input_duration_seconds / 60.0) * 2.0
```

The **2× multiplier** is a conservative buffer — processing time is typically longer than the source video's duration. If you pass `input_duration_seconds` and your balance is below this estimate, the API returns `402` immediately without starting the job.

If `input_duration_seconds` is not provided, the check falls back to `balance > 0`.

This is a guard only — the actual charge is always based on the real inference timer, never the estimate.

```python
result = client.upscale(
    "https://example.com/video.mp4",
    input_duration_seconds=60.0,  # 60s video → ~2 credits estimated
)
```

## Failed jobs

If the inference backend fails (HTTP 502), the job is saved with `status = "failed"` and **no credits are deducted**. The SDK raises `JobFailedError`.

```python
try:
    result = client.upscale("https://example.com/video.mp4")
except xysera.JobFailedError:
    print("Processing failed — you were not charged.")
```

## Topping up

Credits are purchased at [xysera.com](https://xysera.com). The API itself never adds credits — only the web app does.
