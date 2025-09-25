## Comprehensive SDK Audit: Findings and Recommendations

### Summary
This issue captures a full-code audit of the Python SDK, covering packaging, client architecture, API surface, errors, configuration, CLI, tests, typing, documentation, security, and performance. It lists concrete problems, recommended fixes, and a proposed execution plan.

### Impact
- Improves reliability of streaming and non-streaming chat flows
- Aligns versioning, validation, and tests to reduce regressions
- Hardens JSON parsing against API schema drift
- Clarifies docs and security posture; better UX in CLI
- Sets the stage for type-safety and async/throughput improvements

### Key findings
- Version mismatch: `pyproject.toml` declares `0.2.0` while `venice_sdk/__init__.py` sets `__version__ = "1.0.0"`.
- Streaming contract mismatch:
  - `HTTPClient._handle_streaming_response` yields SSE "data: ..." strings.
  - `ChatAPI.complete(stream=True)` expects iterable of dicts and filters `chunk["choices"][0]["delta"]["content"]`.
  - This will break real streaming consumers and diverges from tests/docs expectations.
- Temperature range inconsistency:
  - Docstring/tests indicate 0–1 in places; implementation validates 0–2 (OpenAI-compatible). Align one source of truth.
- Session reuse and convenience functions:
  - Many convenience functions call `load_config()` and create new `VeniceClient`, fragmenting sessions/retry/backoff. Prefer a shared `HTTPClient`/session.
- Models API resilience:
  - `ModelsAPI.list()` returns raw JSON; downstream helpers assume nested keys like `model_spec.capabilities.supportsFunctionCalling`. Add guards/defaults to avoid KeyErrors when API shape changes.
- Image endpoints naming:
  - Mix of `/images/generations` vs `/image/edit` and `/image/upscale`. Normalize endpoint constants and verify server paths.
- Error propagation consistency:
  - `handle_api_error` should consistently include `status_code` on raised exceptions and pass through `retry_after` for 429 based on header/body.
- Typing and mypy:
  - Strict mypy config is present, but many public methods lack annotations; tighten signatures and Optional returns.
- CLI UX/security:
  - Writes `.env` in CWD only. Provide `--global` option (e.g., XDG config) and a `configure` command for `VENICE_BASE_URL`. Warn about committing secrets.
- Docs accuracy and claims:
  - README claims like “350+ tests” and “90%+ pass rate” read as marketing; ensure verifiable or soften.
- Token counting encoder:
  - `tiktoken` default encoder set to `cl100k_base`; expose override to better match non-OpenAI models.
- Performance:
  - Consider `requests` `HTTPAdapter` + `Retry` control; optional async `httpx` client for streaming throughput.

### Recommended changes
- Versioning
  - Use a single source of truth. Either:
    - Keep `__version__` in `venice_sdk/__init__.py` and bump `pyproject.toml` to match; or
    - Adopt dynamic versioning via hatchling and remove hard-coded `__version__`.
- Streaming consistency
  - Standardize on one streaming payload shape (prefer parsed dicts). Either parse SSE in `HTTPClient` to dicts, or make `ChatAPI` parse strings. Ensure `complete(stream=True)` and `complete_stream()` agree.
- Temperature range
  - Choose 0–2 (OpenAI-compatible) or 0–1; update validation, tests, and README consistently.
- HTTP client reuse
  - Refactor convenience functions to accept and reuse a provided `HTTPClient | VeniceClient`, or maintain a shared module-level client/session.
- Models parsing hardening
  - Add `.get()`/defaults for `model_spec` and nested keys; degrade gracefully when capabilities are missing.
- Image endpoint normalization
  - Centralize endpoint paths as constants and align names (`/images/edit`, `/images/upscale`) with server.
- Error handling
  - Ensure `status_code` is always set on `VeniceAPIError` subclasses; propagate `retry_after` from header to body on 429s universally (streaming + non-streaming).
- Typing/mypy
  - Add annotations to public APIs, especially return types that may be `Optional`. Keep exceptions precise.
- CLI enhancements
  - Add `venice configure --base-url ...` and `venice auth --global` (write to `~/.config/venice/.env`). Warn about committing `.env`.
- Docs
  - Audit examples against actual exports/methods; soften unverifiable claims.
- Token utils
  - Expose encoder name override in `utils.count_tokens` or accept an `encoder` param.
- Performance
  - Add `HTTPAdapter` with tuned pool size and `Retry`; evaluate `httpx` async variant for future.

### Proposed implementation plan (checklist)
- [ ] Version sync: unify to single source of truth
- [ ] Streaming contract: make `HTTPClient` and `ChatAPI` agree on chunk shape
- [ ] Temperature validation: pick range, update tests/docs/validation
- [ ] Reuse HTTP session across convenience functions
- [ ] Harden `ModelsAPI` parsing against missing keys
- [ ] Normalize image endpoint constants and verify server paths
- [ ] Enhance `handle_api_error` and 429 `retry_after` injection
- [ ] Add/complete type hints to satisfy mypy config
- [ ] CLI: add `configure`, `--global`, and security warnings
- [ ] README/docs: correct claims and ensure examples run
- [ ] Token counting: encoder override in `utils`
- [ ] Performance: `requests` adapter + retries; consider `httpx` option

### Affected files (non-exhaustive)
- `pyproject.toml`
- `venice_sdk/__init__.py`
- `venice_sdk/client.py`
- `venice_sdk/chat.py`
- `venice_sdk/models.py`
- `venice_sdk/models_advanced.py`
- `venice_sdk/images.py`
- `venice_sdk/errors.py`
- `venice_sdk/utils.py`
- `venice_sdk/cli.py`
- `README.md`

### Notes
If desired, I can submit a PR implementing the first batch (version sync, streaming alignment, temperature range, HTTP client reuse) to reduce risk quickly, followed by API and docs hardening.

