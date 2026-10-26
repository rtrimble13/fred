"""Shared CLI plumbing: state, output selection, error mapping, series-id parsing."""

from __future__ import annotations

import functools
import logging
import re
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import httpx
import typer

from fred.client import FREDClient
from fred.config import SIGNUP_URL, Settings
from fred.errors import ExitCode, FREDConfigError, FREDError
from fred.output import OutputFormat, write_json, write_records
from fred.periods import PeriodError
from fred.records import Record, column_order

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class State:
    """Per-invocation state stored on the Typer context."""

    settings: Settings = field(default_factory=Settings.from_env)
    verbose: int = 0
    quiet: bool = False
    transport: httpx.BaseTransport | None = None  # tests inject a mock transport here


def get_state(ctx: typer.Context) -> State:
    root = ctx.find_root()
    if root.obj is None:
        root.obj = State()
    state: State = root.obj
    return state


def configure_logging(verbose: int) -> None:
    if verbose <= 0:
        return
    logging.basicConfig(
        level=logging.DEBUG, stream=sys.stderr, format="%(name)s: %(message)s", force=True
    )
    if verbose < 2:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)


def warn(state: State, message: str) -> None:
    if not state.quiet:
        sys.stderr.write(f"fred: warning: {message}\n")
        sys.stderr.flush()


def info(state: State, message: str) -> None:
    if not state.quiet:
        sys.stderr.write(f"fred: {message}\n")
        sys.stderr.flush()


def require_api_key(state: State) -> None:
    """Every live request needs a key; fail early with a clear hint when it is missing."""
    if not state.settings.has_api_key:
        raise FREDConfigError(
            "FRED_API_KEY is not set; the FRED API requires a key for every request",
            hint=f"get a free key at {SIGNUP_URL} and export FRED_API_KEY=<32-character key>",
        )


def build_client(state: State) -> FREDClient:
    """Create a client from the current settings (patched by tests)."""
    require_api_key(state)
    return FREDClient.from_settings(
        state.settings, transport=state.transport, on_message=lambda m: warn(state, m)
    )


def resolve_format(
    state: State, fmt: OutputFormat | None, *, allow_table: bool = True
) -> OutputFormat:
    """Pick the output format: flag > FRED_FORMAT > table on a TTY, else JSON."""
    if fmt is not None:
        return fmt
    if state.settings.default_format:
        try:
            return OutputFormat(state.settings.default_format)
        except ValueError as exc:
            raise typer.BadParameter(
                f"FRED_FORMAT={state.settings.default_format!r} is not one of "
                + ", ".join(f.value for f in OutputFormat)
            ) from exc
    if allow_table and sys.stdout.isatty():
        return OutputFormat.TABLE
    return OutputFormat.JSON


def emit_records(
    state: State,
    records: Sequence[Record],
    fmt: OutputFormat,
    output: Path | None,
    *,
    columns: Sequence[str] | None = None,
    title: str | None = None,
) -> None:
    cols = list(columns) if columns else column_order(records)
    write_records(
        records,
        fmt,
        None if output is None else str(output),
        columns=cols,
        title=title,
        no_color=state.settings.no_color,
    )
    if output is not None and str(output) != "-":
        info(state, f"wrote {len(records)} row(s) to {output}")


def emit_json(state: State, obj: Any, output: Path | None) -> None:
    write_json(obj, None if output is None else str(output))
    if output is not None and str(output) != "-":
        info(state, f"wrote {output}")


def handle_errors(func: F) -> F:
    """Map package exceptions to stable exit codes and tidy stderr messages."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except FREDError as exc:
            sys.stderr.write(f"fred: error: {exc.message}\n")
            if exc.hint:
                sys.stderr.write(f"fred: hint: {exc.hint}\n")
            sys.stderr.flush()
            raise typer.Exit(code=int(exc.exit_code)) from exc
        except PeriodError as exc:
            raise typer.BadParameter(str(exc)) from exc
        except BrokenPipeError:  # e.g. `fred data ... | head`
            try:
                sys.stdout.close()
            finally:
                raise typer.Exit(code=int(ExitCode.OK)) from None

    return wrapper  # type: ignore[return-value]


_SPLIT_RE = re.compile(r"[,\s]+")


def collect_series_ids(args: Iterable[str], series_file: Path | None) -> list[str]:
    """Combine positional ids (comma/space separated) with ids from a file or stdin."""
    ids: list[str] = []
    for arg in args:
        ids.extend(p for p in _SPLIT_RE.split(arg) if p)
    if series_file is not None:
        try:
            text = sys.stdin.read() if str(series_file) == "-" else series_file.read_text("utf-8")
        except OSError as exc:
            raise typer.BadParameter(
                f"cannot read series file {series_file}: {exc.strerror or exc}"
            ) from exc
        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if line:
                ids.extend(p for p in _SPLIT_RE.split(line) if p)
    seen: set[str] = set()
    unique: list[str] = []
    for sid in ids:
        key = sid.upper()
        if key not in seen:
            seen.add(key)
            unique.append(key)
    if not unique:
        raise typer.BadParameter(
            "no series ids given (pass them as arguments or via --series-file)"
        )
    return unique


def parse_columns(spec: str | None) -> list[str] | None:
    if not spec:
        return None
    cols = [c.strip() for c in spec.split(",") if c.strip()]
    return cols or None


def select_columns(records: Sequence[Record], requested: Sequence[str] | None) -> list[str]:
    available = column_order(records)
    if not requested:
        return available
    missing = [c for c in requested if c not in available]
    if missing and records:
        raise typer.BadParameter(
            f"unknown column(s): {', '.join(missing)}; available: {', '.join(available)}"
        )
    return list(requested)
