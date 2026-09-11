# Ask Mode Context (Non-Obvious Only)

- The package entry point is `ibm_baw_mcp_server.workflow_mcp_server:cli_main` (declared in `pyproject.toml` under `[project.scripts]`). The server is not run directly — it's invoked as `ibm-baw-mcp-server --transport {stdio|http|sse|streamable-http}`.
- `workflow_client.py` is a thin facade. All HTTP logic lives in `http_client.py`; all OpenAPI retrieval logic lives in `openapi_provider.py`. `WorkflowClient` delegates both via composition/inheritance.
- The server dynamically discovers tools at startup by calling `/bpm/exposed-services` on the BAW instance — there are no statically registered MCP tools. Tool count varies per deployment.
- CSRF token management (2-hour lifetime, 5-minute buffer before expiry) is inside `DirectOpenAPIProvider._ensure_valid_token()` — it is stateful and not thread-safe.
- `tests/test_env.py` `TestEnv` fields are resolved at **class definition time** (not per-test), so changing `TEST_*` env vars between tests in a session has no effect.
