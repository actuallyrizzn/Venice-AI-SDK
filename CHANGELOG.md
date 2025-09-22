# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **Flexible Licensing**: Users can choose between AGPLv3 (strong copyleft) or CC-BY-SA (attribution required)

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