# Authentication

## API keys

All requests to the Xysera API require an API key. Keys have the format:

```
xys_<32 alphanumeric characters>
```

Generate a key at [xysera.com](https://xysera.com). You can create multiple keys and label each one (e.g. `prod`, `staging`, `local-dev`). The label is visible on the `key_label` field of `get_credits()` responses.

## Passing your key to the SDK

Pass the key when constructing a client:

```python
import xysera

client = xysera.Client("xys_...")
```

The SDK sends it as a `Bearer` token on every request:

```
Authorization: Bearer xys_...
```

## Best practices

**Use environment variables.** Never hardcode a key in source code.

```python
import os
import xysera

client = xysera.Client(os.environ["XYSERA_API_KEY"])
```

**Scope keys per environment.** Create separate keys for production, staging, and local development so you can revoke one without affecting others.

**Rotate keys if exposed.** If a key appears in logs, version control, or chat — revoke it immediately from [xysera.com](https://xysera.com) and generate a new one.

## Error responses

| Condition | Exception |
|-----------|-----------|
| Key is valid | Request proceeds normally |
| `Authorization` header missing | `AuthenticationError` (HTTP 403) |
| Key not recognised | `AuthenticationError` (HTTP 401) |

Both 401 and 403 raise `xysera.AuthenticationError`. Check your key format and that the `XYSERA_API_KEY` environment variable is set correctly.

```python
try:
    result = client.upscale("https://example.com/video.mp4")
except xysera.AuthenticationError:
    print("Invalid or missing API key.")
```

See [Error Handling](error-handling.md) for the full exception reference.
