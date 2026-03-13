class XyseraError(Exception):
    """Base exception for all Xysera API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(XyseraError):
    """Raised when the API key is missing or invalid (HTTP 401)."""


class InsufficientCreditsError(XyseraError):
    """Raised when the account has insufficient credits (HTTP 402)."""


class ValidationError(XyseraError):
    """Raised when request parameters are invalid (HTTP 422)."""


class RateLimitError(XyseraError):
    """Raised when the rate limit is exceeded (HTTP 429)."""


class JobFailedError(XyseraError):
    """Raised when the upstream processing job fails (HTTP 502). No credits are charged."""


class ModelUnavailableError(XyseraError):
    """Raised when the requested model is not yet deployed (HTTP 503)."""


class NotFoundError(XyseraError):
    """Raised when the requested resource does not exist or belongs to a different key (HTTP 404)."""
