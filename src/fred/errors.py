"""Exception hierarchy and process exit codes.

Every error raised by this package derives from :class:`FREDError` and carries
an ``exit_code`` so the CLI can map failures to stable, documented exit
statuses (see ``docs/agents.md``).
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Process exit codes used by the ``fred`` CLI."""

    OK = 0
    ERROR = 1  # unexpected / generic failure
    USAGE = 2  # bad arguments (also used by the argument parser)
    API = 3  # the API answered but reported a failure
    QUOTA = 4  # rate limit exceeded (120 requests per minute)
    NETWORK = 5  # transport-level problem: DNS, timeout, TLS, connection reset
    NO_DATA = 6  # --strict was given and at least one series returned nothing
    CONFIG = 7  # missing/invalid configuration (e.g. no FRED_API_KEY)


class FREDError(Exception):
    """Base class for all errors raised by the package."""

    exit_code: ExitCode = ExitCode.ERROR

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint

    def __str__(self) -> str:
        return self.message


class FREDConfigError(FREDError):
    """Configuration is missing or invalid (most often: no or rejected API key)."""

    exit_code = ExitCode.CONFIG


class FREDNetworkError(FREDError):
    """The request never produced an HTTP response."""

    exit_code = ExitCode.NETWORK


class FREDHTTPError(FREDError):
    """The server answered with an unexpected HTTP status or a non-JSON body."""

    exit_code = ExitCode.API

    def __init__(self, status_code: int, message: str, *, hint: str | None = None) -> None:
        super().__init__(message, hint=hint)
        self.status_code = status_code


class FREDAPIError(FREDError):
    """The API rejected the request (HTTP 400/404 with an ``error_message``)."""

    exit_code = ExitCode.API

    def __init__(self, status_code: int, message: str, *, hint: str | None = None) -> None:
        super().__init__(
            f"FRED API error {status_code}: {message or 'no detail provided'}", hint=hint
        )
        self.status_code = status_code
        self.detail = message


class FREDNotFoundError(FREDAPIError):
    """A series, release or category does not exist."""


class FREDQuotaError(FREDError):
    """The per-minute request limit was exceeded (HTTP 429)."""

    exit_code = ExitCode.QUOTA


class FREDNoDataError(FREDError):
    """Raised in ``--strict`` mode when a requested series returned no observations."""

    exit_code = ExitCode.NO_DATA
