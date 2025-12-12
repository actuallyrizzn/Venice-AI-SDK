## Proposed Solution for Issue #49

### Problem
`load_config()` always loads the global .env file when no API key is found, without respecting the `VENICE_USE_GLOBAL_CONFIG` flag. This breaks test isolation.

### Solution
Make `load_config()` respect the `VENICE_USE_GLOBAL_CONFIG` environment variable, matching the behavior of `get_api_key()` and `get_base_url()` in the CLI module.

### Implementation Plan

1. **Update `load_config()` function** in `venice_sdk/config.py`:
   - Add check for `VENICE_USE_GLOBAL_CONFIG` before loading global .env
   - Only load global config if flag is set to truthy value
   - This ensures tests can opt-out of global config loading

2. **Fix `_get_global_config_path()` caching**:
   - Ensure it reads from current environment, not cached module-level values
   - The current implementation already does this, but we should verify

3. **Add test coverage**:
   - Test that `load_config()` respects `VENICE_USE_GLOBAL_CONFIG=0`
   - Test that global config is loaded when flag is set
   - Test that defaults are used when flag is not set and no global config exists

### Code Changes

```python
# In load_config(), replace lines 135-139 with:
api_key = api_key or os.getenv("VENICE_API_KEY")
if not api_key:
    # Only load global config if explicitly enabled
    if os.getenv("VENICE_USE_GLOBAL_CONFIG") in {"1", "true", "TRUE", "yes", "YES"}:
        global_env_path = _get_global_config_path()
        if global_env_path.exists():
            load_dotenv(global_env_path, override=False)
        api_key = os.getenv("VENICE_API_KEY")
if not api_key:
    raise ValueError("API key must be provided")
```

This ensures `load_config()` behavior matches the CLI functions and provides proper test isolation.

