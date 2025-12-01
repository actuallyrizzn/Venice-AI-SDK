# Proposed Solution for Issue #15: CLI Enhancements

## Investigation Summary

After reviewing the codebase, I've confirmed the current state:

1. **Current CLI Implementation** (`venice_sdk/cli.py`):
   - `venice auth <api-key>` only writes to `.env` in current working directory
   - No global configuration support
   - No `venice configure` command for `VENICE_BASE_URL`
   - No security warnings about committing secrets
   - No `venice config` command to view current configuration

2. **Configuration System** (`venice_sdk/config.py`):
   - Already supports `VENICE_BASE_URL` environment variable
   - Uses `load_dotenv()` to load from `.env` files
   - Environment variables take precedence

## Proposed Implementation

### 1. Global Configuration Support
- Add `--global` flag to `venice auth` command
- Use XDG config directory: `~/.config/venice/.env` (or `%APPDATA%\venice\.env` on Windows)
- Maintain backward compatibility with local `.env` files

### 2. New Commands
- `venice configure --base-url <url>`: Set global base URL
- `venice config`: Display current configuration (shows both local and global settings)

### 3. Security Warnings
- Detect if `.env` file is in a git repository
- Warn when creating `.env` files in git-tracked directories
- Warn about insecure base URLs (non-HTTPS)
- Add `.env` to `.gitignore` if it doesn't exist

### 4. Configuration Priority
1. Environment variables (highest priority)
2. Local `.env` file (current directory)
3. Global `.env` file (`~/.config/venice/.env`)

## Implementation Details

### Files to Modify
- `venice_sdk/cli.py`: Add new commands and global config support
- `venice_sdk/config.py`: Update `load_config()` to check global config location
- `tests/test_cli.py`: Add comprehensive tests for new functionality

### New Functions
- `get_global_config_path()`: Returns path to global config directory
- `is_git_repo(path)`: Checks if path is in a git repository
- `warn_about_secrets()`: Displays security warnings
- `read_config_file(path)`: Reads and parses .env file
- `write_config_file(path, key, value)`: Writes to .env file with proper formatting

## Testing Strategy

1. Test global auth command creates config in XDG directory
2. Test local auth command still works (backward compatibility)
3. Test `venice configure` command sets base URL
4. Test `venice config` shows correct configuration priority
5. Test security warnings appear when appropriate
6. Test configuration priority (env > local > global)

## Backward Compatibility

- Existing local `.env` files will continue to work
- Environment variables will still take precedence
- No breaking changes to existing CLI commands

