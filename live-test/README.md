# Live Tests for Venice SDK

This directory contains example tests that demonstrate the Venice SDK's functionality using the live API. These tests are useful for:
- Verifying the SDK works with the actual API
- Demonstrating how to use different SDK features
- Testing error handling and edge cases

## Prerequisites

Before running these tests, ensure you have:
1. A valid Venice API key
2. The API key set in your environment variables or `.env` file
3. Python 3.8+ installed
4. The Venice SDK installed (`pip install -e .` from the project root)

## Running the Tests

You can run the tests individually or all at once:

```bash
# Run all live tests
python -m pytest live-test/

# Run specific test file
python live-test/test_chat_completion.py
python live-test/test_models.py
python live-test/test_error_handling.py
```

## Test Files

### test_chat_completion.py
Demonstrates:
- Basic chat completion
- Streaming chat completion
- Chat completion with tools

### test_models.py
Demonstrates:
- Listing all available models
- Getting details for a specific model
- Filtering for text models only

### test_error_handling.py
Demonstrates:
- Handling invalid API keys
- Handling invalid model names
- Handling invalid message formats
- Connection retry behavior

## Notes

- These tests make actual API calls and will consume your API quota
- Some tests intentionally trigger errors to demonstrate error handling
- The tests include print statements to show what's happening
- You can modify the test parameters to experiment with different settings

## Example Output

When you run the tests, you'll see output like:

```
Running live chat completion tests...
Basic Chat Completion Test:
Response: Hello! I'm doing well, thank you for asking. How can I assist you today?

Streaming Chat Completion Test:
Response chunks:
Once upon a time, there was a curious little cat named Whiskers...

Listing all available models:
Model: Llama 3.3 70B (ID: llama-3.3-70b)
Type: text
Description: A powerful language model
Capabilities:
  - Function Calling: True
  - Web Search: True
  - Context Tokens: 4096
```

## Troubleshooting

If you encounter issues:
1. Verify your API key is correct
2. Check your internet connection
3. Ensure you're using a supported Python version
4. Make sure all dependencies are installed 