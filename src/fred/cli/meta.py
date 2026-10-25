"""Housekeeping commands: ``config``, ``doctor``, ``cache`` and ``version``."""

from __future__ import annotations

import platform
from typing import Annotated, Any

import typer

from fred import __version__
from fred.cache import FileCache
from fred.cli._common import (
    build_client,
    emit_json,
    emit_records,
    get_state,
    handle_errors,
    info,
    resolve_format,
)
from fred.cli.data import FORMAT_OPT, OUTPUT_OPT
from fred.client import LIMITS
from fred.config import (
    API_KEY_LENGTH,
    ENV_API_KEY,
    ENV_BASE_URL,
    ENV_CACHE_DIR,
    ENV_FORMAT,
    ENV_MAX_RETRIES,
    ENV_TIMEOUT,
    ENV_USER_AGENT,
    SIGNUP_URL,
)
from fred.errors import ExitCode, FREDError


def _settings_record(ctx: typer.Context) -> dict[str, Any]:
    s = get_state(ctx).settings
    return {
        "version": __version__,
        "api_key": s.masked_api_key(),
        "api_key_env": ENV_API_KEY,
        "base_url": s.base_url,
        "timeout_seconds": s.timeout,
        "max_retries": s.max_retries,
        "cache_dir": str(s.cache_dir),
        "user_agent": s.user_agent,
        "default_format": s.default_format or ("table on a TTY, json otherwise"),
        "limits": {
            "requests_per_minute": LIMITS.requests_per_minute,
            "observations_per_request": LIMITS.observations_per_request,
            "search_results_per_request": LIMITS.search_results_per_request,
        },
        "environment_variables": [
            ENV_API_KEY,
            ENV_BASE_URL,
            ENV_TIMEOUT,
            ENV_MAX_RETRIES,
            ENV_CACHE_DIR,
            ENV_USER_AGENT,
            ENV_FORMAT,
        ],
    }


def register(app: typer.Typer) -> None:
    @app.command("config", rich_help_panel="Maintenance")
    @handle_errors
    def config(ctx: typer.Context, output: OUTPUT_OPT = None) -> None:
        """Show the effective configuration (the API key is masked)."""
        emit_json(get_state(ctx), _settings_record(ctx), output)

    @app.command("doctor", rich_help_panel="Maintenance")
    @handle_errors
    def doctor(ctx: typer.Context, output: OUTPUT_OPT = None) -> None:
        """Check configuration and live connectivity to the FRED API (costs one request)."""
        state = get_state(ctx)
        report = _settings_record(ctx)
        checks: list[dict[str, Any]] = []
        settings = state.settings
        if not settings.has_api_key:
            key_detail = f"{ENV_API_KEY} not set; the API needs a key ({SIGNUP_URL})"
        elif not settings.api_key_looks_valid:
            key_detail = (
                f"{ENV_API_KEY} is set but does not look like a FRED key "
                f"({API_KEY_LENGTH} lower-case alphanumeric characters)"
            )
        else:
            key_detail = f"{ENV_API_KEY} is set"
        checks.append(
            {"check": "api_key", "ok": settings.api_key_looks_valid, "detail": key_detail}
        )
        exit_code = ExitCode.OK
        if settings.has_api_key:
            try:
                with build_client(state) as client:
                    sources = client.sources()
                checks.append(
                    {
                        "check": "api_reachable",
                        "ok": True,
                        "detail": f"{len(sources)} sources listed",
                    }
                )
            except FREDError as exc:
                checks.append({"check": "api_reachable", "ok": False, "detail": exc.message})
                exit_code = exc.exit_code
        else:
            checks.append({"check": "api_reachable", "ok": False, "detail": "skipped: no API key"})
            exit_code = ExitCode.CONFIG
        checks.append(
            {
                "check": "python",
                "ok": True,
                "detail": f"{platform.python_version()} on {platform.system()}",
            }
        )
        report["checks"] = checks
        report["healthy"] = all(c["ok"] for c in checks)
        emit_json(state, report, output)
        if not report["healthy"]:
            raise typer.Exit(code=int(exit_code or ExitCode.NETWORK))

    cache_app = typer.Typer(help="Manage the local metadata cache.", no_args_is_help=True)
    app.add_typer(cache_app, name="cache", rich_help_panel="Maintenance")

    @cache_app.command("info")
    @handle_errors
    def cache_info(ctx: typer.Context, fmt: FORMAT_OPT = None, output: OUTPUT_OPT = None) -> None:
        """List cached files."""
        state = get_state(ctx)
        root = state.settings.cache_dir
        records = []
        if root.is_dir():
            for p in sorted(root.rglob("*")):
                if p.is_file():
                    records.append({"file": str(p.relative_to(root)), "bytes": p.stat().st_size})
        emit_records(state, records, resolve_format(state, fmt), output, title=f"cache: {root}")

    @cache_app.command("clear")
    @handle_errors
    def cache_clear(ctx: typer.Context) -> None:
        """Delete all cached metadata (releases, categories)."""
        state = get_state(ctx)
        removed = FileCache(state.settings.cache_dir).clear()
        info(state, f"removed {removed} cached file(s) from {state.settings.cache_dir}")

    @app.command("version", rich_help_panel="Maintenance")
    def version(
        short: Annotated[
            bool, typer.Option("--short", help="Print only the version number.")
        ] = False,
    ) -> None:
        """Print the version."""
        if short:
            typer.echo(__version__)
        else:
            typer.echo(f"fred {__version__} (python {platform.python_version()})")
