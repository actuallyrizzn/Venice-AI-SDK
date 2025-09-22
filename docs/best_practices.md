# Best Practices

This guide covers best practices for using the Venice AI SDK effectively in production applications.

## 🔐 Security

### API Key Management

**✅ Do:**
```python
import os
from venice_sdk import VeniceClient

# Use environment variables
api_key = os.getenv("VENICE_API_KEY")
client = VeniceClient(api_key=api_key)

# Or use .env files
from dotenv import load_dotenv
load_dotenv()
client = VeniceClient()
```

**❌ Don't:**
```python
# Never hardcode API keys
client = VeniceClient(api_key="sk-1234567890abcdef")  # BAD!

# Don't commit API keys to version control
# Don't log API keys
print(f"Using API key: {api_key}")  # BAD!
```

### Key Rotation

**✅ Do:**
```python
# Implement key rotation
def rotate_api_key():
    # Generate new key
    new_key = client.api_keys.create(
        name="rotated-key",
        permissions=["read", "write"]
    )
    
    # Update environment
    os.environ["VENICE_API_KEY"] = new_key.api_key
    
    # Delete old key
    client.api_keys.delete(old_key_id)
```

### Input Validation

**✅ Do:**
```python
def safe_chat_completion(messages, model="llama-3.3-70b"):
    # Validate input
    if not messages or not isinstance(messages, list):
        raise ValueError("Messages must be a non-empty list")
    
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Each message must be a dictionary")
        if "role" not in message or "content" not in message:
            raise ValueError("Messages must have 'role' and 'content'")
    
    # Sanitize content
    for message in messages:
        message["content"] = sanitize_input(message["content"])
    
    return client.chat.complete(messages=messages, model=model)

def sanitize_input(text):
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", '"', "'"]
    for char in dangerous_chars:
        text = text.replace(char, "")
    
    # Limit length
    return text[:10000]  # Adjust based on your needs
```

## ⚡ Performance

### Caching

**✅ Do:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_embeddings(text):
    """Cache embeddings to avoid redundant API calls."""
    return client.embeddings.generate([text])[0]

def get_embedding(text):
    # Create cache key
    cache_key = hashlib.md5(text.encode()).hexdigest()
    return cached_embeddings(text)
```

### Batch Processing

**✅ Do:**
```python
# Process multiple items in batches
def process_texts_batch(texts, batch_size=10):
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Process batch
        batch_results = client.embeddings.generate(batch)
        results.extend(batch_results)
        
        # Rate limiting
        time.sleep(0.1)  # Adjust based on your rate limits
    
    return results
```

### Streaming

**✅ Do:**
```python
def stream_with_progress(messages, model="llama-3.3-70b"):
    """Stream responses with progress indication."""
    total_tokens = 0
    
    for chunk in client.chat.complete_stream(
        messages=messages,
        model=model
    ):
        if chunk.startswith("data: "):
            data_content = chunk[6:].strip()
            if data_content == "[DONE]":
                break
            
            try:
                data = json.loads(data_content)
                if "choices" in data and data["choices"]:
                    delta = data["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        print(content, end="", flush=True)
                        total_tokens += len(content.split())
            except json.JSONDecodeError:
                pass
    
    print(f"\n\nGenerated {total_tokens} tokens")
```

## 🛡️ Error Handling

### Comprehensive Error Handling

**✅ Do:**
```python
import time
from venice_sdk.errors import VeniceAPIError, RateLimitError, UnauthorizedError

def robust_api_call(func, max_retries=3, backoff_factor=2):
    """Make API calls with retry logic."""
    for attempt in range(max_retries):
        try:
            return func()
        
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise
        
        except UnauthorizedError as e:
            print("Authentication failed. Check your API key.")
            raise
        
        except VeniceAPIError as e:
            if e.status_code >= 500:  # Server errors
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"Server error. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
            else:  # Client errors
                raise
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    raise Exception("Max retries exceeded")

# Usage
def chat_with_retry(messages, model="llama-3.3-70b"):
    return robust_api_call(
        lambda: client.chat.complete(messages=messages, model=model)
    )
```

### Graceful Degradation

**✅ Do:**
```python
def fallback_chat(messages, primary_model="llama-3.3-70b", fallback_model="llama-3.3-8b"):
    """Try primary model, fallback to secondary if it fails."""
    try:
        return client.chat.complete(messages=messages, model=primary_model)
    except VeniceAPIError as e:
        if e.status_code == 404:  # Model not found
            print(f"Primary model {primary_model} not available, trying {fallback_model}")
            return client.chat.complete(messages=messages, model=fallback_model)
        else:
            raise
```

## 📊 Monitoring and Logging

### Structured Logging

**✅ Do:**
```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_api_call(endpoint, model, tokens_used, duration, success=True):
    """Log API calls with structured data."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "model": model,
        "tokens_used": tokens_used,
        "duration_ms": duration * 1000,
        "success": success
    }
    
    logger.info(json.dumps(log_data))

# Usage in your code
start_time = time.time()
try:
    response = client.chat.complete(messages=messages, model=model)
    duration = time.time() - start_time
    
    # Estimate tokens (in production, use actual token count)
    tokens_used = len(" ".join([m["content"] for m in messages]).split())
    
    log_api_call("chat/completions", model, tokens_used, duration, True)
    
except Exception as e:
    duration = time.time() - start_time
    log_api_call("chat/completions", model, 0, duration, False)
    raise
```

### Usage Tracking

**✅ Do:**
```python
class UsageTracker:
    def __init__(self):
        self.usage = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "by_model": {}
        }
    
    def track_request(self, model, tokens, cost=0.0):
        """Track API usage."""
        self.usage["total_requests"] += 1
        self.usage["total_tokens"] += tokens
        self.usage["total_cost"] += cost
        
        if model not in self.usage["by_model"]:
            self.usage["by_model"][model] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        
        self.usage["by_model"][model]["requests"] += 1
        self.usage["by_model"][model]["tokens"] += tokens
        self.usage["by_model"][model]["cost"] += cost
    
    def get_usage_summary(self):
        """Get usage summary."""
        return self.usage.copy()

# Usage
tracker = UsageTracker()

def tracked_chat(messages, model="llama-3.3-70b"):
    response = client.chat.complete(messages=messages, model=model)
    
    # Track usage (simplified - in production, get actual token count)
    tokens = len(" ".join([m["content"] for m in messages]).split())
    tracker.track_request(model, tokens)
    
    return response
```

## 🔄 Rate Limiting

### Intelligent Rate Limiting

**✅ Do:**
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove requests older than 1 minute
        while self.requests and self.requests[0] <= now - 60:
            self.requests.popleft()
        
        # If we're at the limit, wait
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Record this request
        self.requests.append(now)

# Usage
rate_limiter = RateLimiter(requests_per_minute=50)

def rate_limited_chat(messages, model="llama-3.3-70b"):
    rate_limiter.wait_if_needed()
    return client.chat.complete(messages=messages, model=model)
```

## 🧪 Testing

### Unit Testing

**✅ Do:**
```python
import unittest
from unittest.mock import patch, MagicMock
from venice_sdk import VeniceClient

class TestVeniceSDK(unittest.TestCase):
    def setUp(self):
        self.client = VeniceClient(api_key="test-key")
    
    @patch('venice_sdk.client.HTTPClient.get')
    def test_chat_completion(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }
        mock_get.return_value = mock_response
        
        # Test the function
        response = self.client.chat.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.3-70b"
        )
        
        # Assertions
        self.assertEqual(response.choices[0].message.content, "Hello!")
        mock_get.assert_called_once()
    
    def test_input_validation(self):
        with self.assertRaises(ValueError):
            self.client.chat.complete(messages=[], model="llama-3.3-70b")
        
        with self.assertRaises(ValueError):
            self.client.chat.complete(
                messages=[{"role": "user"}],  # Missing content
                model="llama-3.3-70b"
            )

if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

**✅ Do:**
```python
import pytest
from venice_sdk import VeniceClient

@pytest.mark.live
class TestLiveIntegration:
    def test_chat_completion_live(self):
        """Test with real API calls."""
        client = VeniceClient()
        
        response = client.chat.complete(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.3-70b"
        )
        
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0
    
    def test_image_generation_live(self):
        """Test image generation with real API."""
        client = VeniceClient()
        
        result = client.images.generate(
            prompt="A simple test image",
            model="dall-e-3"
        )
        
        assert result.url is not None or result.b64_json is not None
```

## 🚀 Production Deployment

### Configuration Management

**✅ Do:**
```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductionConfig:
    api_key: str
    base_url: str = "https://api.venice.ai/api/v1"
    timeout: int = 30
    max_retries: int = 3
    rate_limit_rpm: int = 60
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("VENICE_API_KEY"),
            base_url=os.getenv("VENICE_BASE_URL", "https://api.venice.ai/api/v1"),
            timeout=int(os.getenv("VENICE_TIMEOUT", "30")),
            max_retries=int(os.getenv("VENICE_MAX_RETRIES", "3")),
            rate_limit_rpm=int(os.getenv("VENICE_RATE_LIMIT_RPM", "60"))
        )

# Usage
config = ProductionConfig.from_env()
client = VeniceClient(
    api_key=config.api_key,
    base_url=config.base_url,
    timeout=config.timeout
)
```

### Health Checks

**✅ Do:**
```python
def health_check():
    """Check if the API is healthy."""
    try:
        # Simple API call to check connectivity
        models = client.models.list()
        return {
            "status": "healthy",
            "models_available": len(models) > 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Use in your application
@app.route("/health")
def health_endpoint():
    return jsonify(health_check())
```

## 📈 Performance Optimization

### Connection Pooling

**✅ Do:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_optimized_client():
    """Create a client with optimized connection settings."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Configure adapter
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return VeniceClient(http_session=session)
```

### Async Operations

**✅ Do:**
```python
import asyncio
import aiohttp

async def async_chat_completion(messages, model="llama-3.3-70b"):
    """Async chat completion."""
    async with aiohttp.ClientSession() as session:
        # Use async HTTP client
        # Implementation depends on your async setup
        pass

# Batch processing with asyncio
async def process_batch_async(texts):
    """Process multiple texts concurrently."""
    tasks = []
    for text in texts:
        task = asyncio.create_task(process_single_text(text))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## 🎯 Summary

### Key Principles

1. **Security First**: Never hardcode API keys, always validate input
2. **Error Handling**: Implement comprehensive error handling and retry logic
3. **Performance**: Use caching, batching, and rate limiting
4. **Monitoring**: Log everything and track usage
5. **Testing**: Write comprehensive tests for all functionality
6. **Configuration**: Use environment variables for configuration
7. **Documentation**: Document your code and keep it updated

### Quick Checklist

- [ ] API keys stored securely
- [ ] Input validation implemented
- [ ] Error handling with retries
- [ ] Rate limiting configured
- [ ] Logging and monitoring set up
- [ ] Tests written and passing
- [ ] Configuration externalized
- [ ] Performance optimized
- [ ] Security reviewed
- [ ] Documentation updated

Following these best practices will help you build robust, scalable applications with the Venice AI SDK.
