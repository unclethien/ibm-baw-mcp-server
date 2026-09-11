# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

Python 3.12, managed with **uv** (not pip/poetry). Single runtime dependency: `fastmcp==3.2.0`.

## Commands

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests (generates reports in reports/junit/ and reports/html/)
uv run pytest

# Run a single test file
uv run pytest tests/client/test_http_client.py

# Run a single test function
uv run pytest tests/client/test_http_client.py::TestBaseHTTPClient::test_init_with_username_password

# Lint
uv run ruff check src tests

# Format
uv run ruff format src tests

# Type check
uv run mypy src
```

## Critical gotchas

- **pytest auto-generates reports** to `reports/junit/` and `reports/html/` on every run (`pytest.ini` hardcodes `--junitxml` and `--html`). The `reports/` directory must exist or tests fail.
- **`NO_TIMEOUT_PROVIDED` sentinel** (`utils.py`): `HTTPConnectionConfig.timeout` uses a module-level sentinel object (not `None`) to distinguish "no timeout kwarg passed" from "explicitly disable timeout". Never pass `None` when you mean "use default"; check for the sentinel before passing timeout to httpx.
- **`conftest.py` blocks all real network calls** via an `autouse` fixture that patches httpx methods — any test touching real HTTP will raise `RuntimeError`. All tests must mock HTTP calls.
- **Test credentials** are centralized in `tests/test_env.py` (`TestEnv` class) and re-exported through `tests/client/test_fixtures.py` (`MockCredentials`). Override with `TEST_ENDPOINT`, `TEST_USERNAME`, etc. env vars.
- **`src/` is not on `PYTHONPATH` by default** — `conftest.py` injects it via `sys.path.insert`. Tests import from `ibm_baw_mcp_server.*` (not `src.ibm_baw_mcp_server.*`).
- **`show_banner=False`** must be passed to `main_mcp.run()` — FastMCP's banner can trigger `PermissionError` trying to read system files in restricted environments.
- **FastMCP server mounts**: each BAW process app's OpenAPI spec becomes a separate mounted `FastMCP` sub-server with a namespace of `{process_app_short_name}_{sanitized_api_title}`.

## Code style

- **Ruff** enforces: `E`, `F`, `I` (isort), `N`, `B`, `W`, `C90`, `UP`, `PL`, `RUF`. Line length 88, double quotes.
- **mypy** with `disallow_untyped_defs = true` — all functions must have type annotations.
- Logging: use `logging.getLogger(__name__)` per module. Never log raw credentials; use `_sanitize_url_for_logging` / `_sanitize_headers_for_logging` before logging URLs/headers.
- Error pattern: `raise ValueError("message") from e` when re-raising with context.
- Apache 2.0 license header required on every source file.
