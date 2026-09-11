# Agent Coding Rules (Non-Obvious Only)

- `NO_TIMEOUT_PROVIDED` in `src/ibm_baw_mcp_server/utils.py` is a sentinel object — not `None`. When building `request_kwargs` for httpx, omit the `timeout` key entirely when the value is this sentinel. Do not substitute `None` (that means "disable timeout").
- All new HTTP methods on `BaseHTTPClient` must replicate the three-branch timeout logic (sentinel = omit key, `None` = pass `None`, float = pass value).
- When adding a new source module, add the Apache 2.0 license header block before any code.
- Tool namespaces in the mounted FastMCP servers are auto-generated as `{process_app_short_name}_{replace_invalid_characters(api_title)}`. `replace_invalid_characters` is in `utils.py` — use it for any user-facing namespace/identifier derived from BAW API data.
- Tests that need HTTP responses must mock at `httpx.get` / `httpx.post` / etc. (module-level functions), not on client instances, because `conftest.py`'s autouse fixture patches those specific attributes.
- New test files in `tests/client/` must import `from tests.client.test_fixtures import MockCredentials` for credential constants — never hardcode credentials.
- `WorkflowClient` uses multiple inheritance: `BaseHTTPClient` + `OpenAPIProvider`. Any new provider implementation must subclass `OpenAPIProvider` (abstract) and accept a `BaseHTTPClient` instance, not a `WorkflowClient`.
