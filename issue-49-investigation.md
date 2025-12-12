## Investigation Results for Issue #49

### Current Status
**Issue #49 is VALID** - `load_config()` does not respect the `VENICE_USE_GLOBAL_CONFIG` flag, causing test isolation problems.

### Problem Analysis

1. **CLI functions respect the flag**: `get_api_key()` and `get_base_url()` in `venice_sdk/cli.py` correctly check `VENICE_USE_GLOBAL_CONFIG` before loading global config (lines 109, 136).

2. **load_config() ignores the flag**: The `load_config()` function in `venice_sdk/config.py` (lines 135-139) always loads the global .env file when no API key is found, without checking `VENICE_USE_GLOBAL_CONFIG`.

3. **Test isolation**: While `conftest.py` sets `XDG_CONFIG_HOME` to a temp directory (line 17), this only works if the config path is recalculated. The cached `_CACHED_XDG_CONFIG_HOME` in `config.py` (line 10) might cause issues.

### Impact

- Tests that clear environment variables still get values from global config
- `test_status_command_without_key` might pass due to temp XDG_CONFIG_HOME, but `load_config()` could still load real global config
- `test_load_config_defaults` might get base_url from global config instead of defaults

### Proposed Solution

1. Make `load_config()` respect `VENICE_USE_GLOBAL_CONFIG` flag (similar to CLI functions)
2. Ensure `_get_global_config_path()` uses current environment, not cached values
3. Add tests to verify global config isolation

### Code Changes Needed

1. Update `load_config()` to check `VENICE_USE_GLOBAL_CONFIG` before loading global .env
2. Ensure `_get_global_config_path()` reads from current environment
3. Add test coverage for global config opt-out behavior

