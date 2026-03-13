"""
Xysera SDK — quick-start example.

1. Install:  pip install xysera
2. Set your API key:
       export XYSERA_API_KEY="xys_..."
   or replace os.environ["XYSERA_API_KEY"] below with your key string.
3. Run:  python example.py
"""

import os
import xysera

# ---------------------------------------------------------------------------
# Configuration — edit these two values before running
# ---------------------------------------------------------------------------
API_KEY   = os.environ.get("XYSERA_API_KEY", "xys_your_api_key_here")
INPUT_URL = "https://www.w3schools.com/html/mov_bbb.mp4"
# ---------------------------------------------------------------------------

client = xysera.Client(API_KEY)

# Check your credit balance
credits = client.get_credits()
print(f"Credits remaining: {credits.credits_balance}  (key: {credits.key_label})")

# Upscale a video or image
# scale=4 and model="RealESRGAN_x4plus" are the defaults — shown here explicitly
print("\nSubmitting upscale job (this may take a few minutes)...")
try:
    result = client.upscale(
        INPUT_URL,
        scale=4,
        model="RealESRGAN_x4plus",
    )
except xysera.AuthenticationError:
    raise SystemExit("Invalid API key — check your XYSERA_API_KEY.")
except xysera.InsufficientCreditsError:
    raise SystemExit("Not enough credits — top up at xysera.com.")
except xysera.JobFailedError:
    raise SystemExit("Processing failed — no credits were charged. Try again.")
except xysera.ModelUnavailableError:
    raise SystemExit("Model is not yet available. Try RealESRGAN_x4plus.")
except xysera.XyseraError as e:
    raise SystemExit(f"API error (HTTP {e.status_code}): {e}")

print(f"Done!")
print(f"  job_id:          {result.job_id}")
print(f"  credits_charged: {result.credits_charged}")
print(f"  processing_time: {result.processing_time}s")
if result.hit_cold_start:
    print(f"  cold_start_time: {result.cold_start_time}s (endpoint was cold — not billed)")
print(f"  result_url:      {result.result_url}  (valid for 1 hour)")

# Download the result to disk
output_path = result.download("output.mp4")
print(f"\nSaved to: {output_path}")
