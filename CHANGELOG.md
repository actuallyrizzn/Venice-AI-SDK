# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Clarified that `VideoAPI.complete()` is the sync queue+wait helper (music-parity). Venice job cleanup is `VideoAPI.cleanup()` → `POST /video/complete` (#66).

### Changed
- `VideoAPI.get_valid_parameters()` now probes the full duration × aspect_ratio grid and returns `combinations` with every valid pair (#65).

### Tests
- Unit + integration coverage of `venice_sdk` brought to 100%.

## [0.3.1] - 2026-08-13

### Fixed
- Image upscale/styles paths: use live Venice routes `/image/upscale` and `/image/styles` (plural `/images/...` returned 404).
- Billing summary: `/billing/summary` removed from Venice; `get_billing_summary()` now uses `/billing/balance` with usage fallback.
- Documented that `GET /models/traits` exists; added `ModelsTraitsAPI.get_trait_categories()`.

### Added
- Multipart POST support on `HTTPClient.post_multipart` (transcriptions, voice clone, text-parser).
- `POST /responses` via `client.responses` (`ResponsesAPI`).
- `POST /audio/transcriptions` (`AudioAPI.transcribe`) and `POST /audio/voices` (`AudioAPI.clone_voice`).
- `POST /video/transcriptions` (`VideoAPI.transcribe`).
- Venice-native `POST /image/generate` (`ImageAPI.generate_native`).
- Augment tools: `client.augment.search|scrape|parse_text`.
- Billing: `get_balance`, `get_usage_analytics`, `get_usage_history`.
- Character reviews: `CharactersAPI.reviews`.
- Crypto RPC: `client.crypto.networks|rpc`.
- x402: `client.x402.balance|top_up|transactions`.
- Chat: multimodal/`tool` roles; first-class `reasoning`, `tool_choice`, `response_format`, `top_p`/`top_k`, etc.
- Parity inventory: `docs/dev/API-PARITY-GAP-2026-08-13.md`.

## [0.3.0] - 2026-03-19

### Added
- **Image multi-edit**: `ImageEditAPI.multi_edit()` and `multi_edit_image()` for editing with 1–3 layered images (base + masks/overlays) via `/image/multi-edit`.
- **Image background remove**: `ImageEditAPI.remove_background()` and `remove_background()` for AI background removal via `/image/background-remove`.
- **Music generation API**: `MusicAPI` with `queue()`, `retrieve()`, `quote()`, and `complete()` for async music/sound-effect generation (`/audio/queue`, `/audio/retrieve`, `/audio/quote`, `/audio/complete`). Exposed as `client.music`.
- **TEE API**: `TEEAPI` with `attestation()` and `signature()` for Trusted Execution Environment verification. Exposed as `client.tee`.
- **Chat**: Optional `prompt_cache_key` parameter for prompt caching, and expanded docstring for `venice_parameters` (e.g. `enable_web_search`, `enable_web_scraping`, `enable_x_search`, `strip_thinking_response`, `disable_thinking`, `enable_web_citations`, etc.).

### Changed
- Endpoints: added `ImageEndpoints.MULTI_EDIT`, `BACKGROUND_REMOVE`; `AudioEndpoints.QUEUE`, `RETRIEVE`, `QUOTE`, `COMPLETE`; `TEEEndpoints.ATTESTATION`, `SIGNATURE`.

## [0.2.1] - 2025-01-22

### Changed
- Added explicit upper bounds to all runtime, developer, documentation, and publishing dependencies to prevent breaking changes from surprise major upgrades.
- Documented the new dependency version policy in `docs/installation.md` so contributors understand how we validate new ranges.

### Added
- **Token Counting Encoder Override**: Added optional `encoder` and `model` parameters to `count_tokens()` function for flexible token counting
- **Centralized Endpoint Constants**: Created `venice_sdk/endpoints.py` module for consistent API endpoint management
- **Enhanced Error Handling**: Improved fallback mechanisms for invalid encoders in token counting

### Changed
- **Image Endpoint Consistency**: Standardized all image API endpoints to use `/images/` prefix for consistency
- **Temperature Documentation**: Updated all temperature range documentation to consistently show 0-2 range
- **Test Statistics**: Updated README with accurate test count (1069 tests) and pass rate (100%)

### Fixed
- **Unicode Compatibility**: Fixed Unicode characters in examples for Windows console compatibility
- **Documentation Accuracy**: Corrected misleading test statistics and claims in README
- **Cross-Platform Support**: Improved example compatibility across different operating systems

## [0.2.0] - 2025-01-22

### Added
- **Admin API Key Management**: Full support for creating, listing, and deleting API keys
- **Advanced Billing Management**: Comprehensive usage tracking, rate limiting, and billing summaries
- **Enhanced Error Handling**: Improved error messages and validation throughout the SDK
- **Streaming Chat Support**: Proper Server-Sent Events (SSE) handling for real-time chat responses
- **Image Generation Enhancements**: Support for data URLs and improved file handling
- **Comprehensive Test Suite**: 350+ tests with 90%+ pass rate including live API tests
- **Input Validation**: Robust parameter validation for all API endpoints
- **Timeout Handling**: Graceful handling of API timeouts and rate limits
- **Multiple API Key Support**: Support for both admin and inference-only API keys

### Changed
- **API Response Parsing**: Updated to match actual Venice AI API response structures
- **Model Capabilities**: Fixed capability mapping to use correct API capability names
- **Data Structures**: Aligned all data classes with actual API response formats
- **Error Messages**: Improved error messages for better debugging and user experience
- **Test Infrastructure**: Enhanced test isolation and cleanup to prevent interference

### Fixed
- **Connection Issues**: Resolved fake URL connection errors in test suite
- **Authentication**: Fixed admin API key authentication and permission handling
- **Rate Limiting**: Corrected rate limit parsing from nested API response structure
- **Usage Tracking**: Fixed billing and usage data parsing from array-based responses
- **Image Handling**: Fixed base64 import issues and data URL support
- **Chat Streaming**: Corrected SSE format handling for streaming responses
- **CLI Functionality**: Fixed Click command invocation and Unicode handling on Windows
- **Environment Management**: Improved .env file handling and environment variable restoration
- **Test Assertions**: Updated hundreds of test assertions to match actual API behavior

### Security
- **API Key Validation**: Enhanced validation and error handling for API key operations
- **Input Sanitization**: Added comprehensive input validation to prevent invalid API calls
- **Error Handling**: Improved error handling to prevent sensitive information leakage

### License
- **Dual License**: Changed from CC-BY-SA 4.0 to dual license (AGPLv3 + CC-BY-SA 4.0)
- **Code/Software**: GNU Affero General Public License v3.0 (AGPLv3) - Strong copyleft protection
- **Documentation/Examples**: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA) - Attribution required

## [0.1.0] - 2024-03-20

### Added
- Initial release of the Venice SDK
- Core HTTP client with retry logic and error handling
- Chat completion API with streaming support
- Function calling/tools support
- Model discovery functionality
- CLI for managing API credentials
- Comprehensive documentation
- Test suite with live tests
- Environment variable and .env file support

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release) 