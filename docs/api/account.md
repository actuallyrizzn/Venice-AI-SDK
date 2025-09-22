# Account Management API

The Account Management API provides comprehensive access to account-related functionality including API key management, billing information, and usage tracking.

## Overview

The Account Management API is split into several specialized classes:

- **`APIKeysAPI`** - API key creation, listing, and management
- **`BillingAPI`** - Usage tracking, billing summaries, and rate limits
- **`AccountManager`** - High-level account management and summaries

## API Keys Management

### APIKeysAPI

The `APIKeysAPI` class handles all API key operations.

```python
from venice_sdk import VeniceClient

client = VeniceClient()
api_keys = client.api_keys  # APIKeysAPI instance
```

#### Methods

##### `list() -> List[APIKey]`

List all API keys associated with your account.

```python
keys = api_keys.list()
for key in keys:
    print(f"Key: {key.name} ({key.id})")
    print(f"  Type: {key.permissions.get('type', 'Unknown')}")
    print(f"  Created: {key.created_at}")
    print(f"  Active: {key.is_active}")
```

**Returns:**
- `List[APIKey]` - List of API key objects

**Raises:**
- `APIKeyError` - If the request fails
- `UnauthorizedError` - If admin permissions are required

##### `get(key_id: str) -> Optional[APIKey]`

Get a specific API key by ID.

```python
key = api_keys.get("key-123")
if key:
    print(f"Found key: {key.name}")
else:
    print("Key not found")
```

**Parameters:**
- `key_id` (str) - The ID of the API key to retrieve

**Returns:**
- `Optional[APIKey]` - API key object if found, None otherwise

##### `create(name: str, permissions: Optional[List[str]] = None, expires_in_days: Optional[int] = None) -> APIKey`

Create a new API key.

```python
# Create an inference-only key
new_key = api_keys.create(
    name="My New Key",
    permissions=["read", "write"]
)

# Create an admin key
admin_key = api_keys.create(
    name="Admin Key",
    permissions=["admin"]
)

print(f"Created key: {new_key.id}")
print(f"API Key: {new_key.api_key}")  # Only available immediately after creation
```

**Parameters:**
- `name` (str) - Name for the API key
- `permissions` (Optional[List[str]]) - List of permissions (not used by API)
- `expires_in_days` (Optional[int]) - Expiration in days (not used by API)

**Returns:**
- `APIKey` - New API key object

**Raises:**
- `APIKeyError` - If creation fails
- `UnauthorizedError` - If admin permissions are required

##### `delete(key_id: str) -> bool`

Delete an API key.

```python
success = api_keys.delete("key-123")
if success:
    print("Key deleted successfully")
else:
    print("Failed to delete key")
```

**Parameters:**
- `key_id` (str) - The ID of the API key to delete

**Returns:**
- `bool` - True if successful, False otherwise

**Raises:**
- `APIKeyError` - If deletion fails
- `UnauthorizedError` - If admin permissions are required

##### `update(key_id: str, name: Optional[str] = None, permissions: Optional[List[str]] = None) -> Optional[APIKey]`

Update an API key (not supported via SDK).

```python
try:
    updated_key = api_keys.update("key-123", name="Updated Name")
except APIKeyError as e:
    print(f"Update not supported: {e}")
```

**Note:** API key updating is not supported via the SDK. Please use the Venice AI web interface.

##### `get_rate_limits() -> RateLimits`

Get current rate limit information.

```python
limits = api_keys.get_rate_limits()
print(f"Requests per minute: {limits.requests_per_minute}")
print(f"Tokens per minute: {limits.tokens_per_minute}")
print(f"Current usage: {limits.current_usage}")
```

**Returns:**
- `RateLimits` - Current rate limit information

##### `get_rate_limits_log(limit: Optional[int] = None) -> List[RateLimitLog]`

Get rate limit violation logs.

```python
logs = api_keys.get_rate_limits_log(limit=10)
for log in logs:
    print(f"Rate limit exceeded at {log.timestamp}")
    print(f"Endpoint: {log.endpoint}")
    print(f"Error type: {log.error_type}")
```

**Parameters:**
- `limit` (Optional[int]) - Maximum number of log entries to return

**Returns:**
- `List[RateLimitLog]` - List of rate limit log entries

## Billing Management

### BillingAPI

The `BillingAPI` class handles billing and usage information.

```python
billing = client.billing  # BillingAPI instance
```

#### Methods

##### `get_usage() -> UsageInfo`

Get current account usage information.

```python
usage = billing.get_usage()
print(f"Total usage: {usage.total_usage}")
print(f"Credits remaining: {usage.credits_remaining}")
print(f"Current period: {usage.current_period}")

# Usage by model
for model, model_usage in usage.usage_by_model.items():
    print(f"{model}: {model_usage['requests']} requests, {model_usage['cost']} cost")
```

**Returns:**
- `UsageInfo` - Current usage information

##### `get_usage_by_model() -> Dict[str, ModelUsage]`

Get detailed usage information by model.

```python
model_usage = billing.get_usage_by_model()
for model_id, usage in model_usage.items():
    print(f"Model: {usage.model_id}")
    print(f"  Requests: {usage.requests}")
    print(f"  Tokens: {usage.tokens}")
    print(f"  Cost: {usage.cost}")
```

**Returns:**
- `Dict[str, ModelUsage]` - Usage information grouped by model

##### `get_billing_summary() -> Dict[str, Any]`

Get comprehensive billing summary.

```python
summary = billing.get_billing_summary()
print(f"Current balance: {summary.get('current_balance', 'N/A')}")
print(f"Total spent: {summary.get('total_spent', 'N/A')}")
print(f"Subscription status: {summary.get('subscription_status', 'N/A')}")
```

**Returns:**
- `Dict[str, Any]` - Billing summary information

##### `get_credits_remaining() -> int`

Get remaining credits.

```python
credits = billing.get_credits_remaining()
print(f"Credits remaining: {credits}")
```

**Returns:**
- `int` - Number of credits remaining

##### `get_total_usage() -> int`

Get total usage amount.

```python
total = billing.get_total_usage()
print(f"Total usage: {total}")
```

**Returns:**
- `int` - Total usage amount

## Account Manager

### AccountManager

The `AccountManager` class provides high-level account management functionality.

```python
account = client.account  # AccountManager instance
```

#### Methods

##### `get_account_summary() -> Dict[str, Any]`

Get a comprehensive account summary.

```python
summary = account.get_account_summary()

if "api_keys" in summary:
    print(f"API Keys: {len(summary['api_keys'])}")
    
if "usage" in summary:
    usage = summary["usage"]
    print(f"Total usage: {usage.get('total_usage', 'N/A')}")
    
if "rate_limits" in summary:
    limits = summary["rate_limits"]
    print(f"Rate limits: {limits}")
```

**Returns:**
- `Dict[str, Any]` - Account summary information

##### `check_rate_limit_status() -> Dict[str, Any]`

Check current rate limit status.

```python
status = account.check_rate_limit_status()
print(f"Status: {status.get('status', 'unknown')}")
print(f"Message: {status.get('message', 'No message')}")

if "current_usage" in status:
    usage = status["current_usage"]
    print(f"Current usage: {usage}")
```

**Returns:**
- `Dict[str, Any]` - Rate limit status information

## Data Classes

### APIKey

Represents an API key.

```python
@dataclass
class APIKey:
    id: str
    name: str
    description: Optional[str]
    created_at: Optional[Union[str, int]]
    last_used: Optional[Union[str, int]]
    is_active: bool
    permissions: Dict[str, Any]
    rate_limits: Optional[Dict[str, Any]]
```

### UsageInfo

Represents usage information.

```python
@dataclass
class UsageInfo:
    total_usage: int
    current_period: str
    credits_remaining: int
    usage_by_model: Dict[str, Dict[str, Any]]
    billing_period_start: Optional[Union[str, int]]
    billing_period_end: Optional[Union[str, int]]
```

### RateLimits

Represents rate limit information.

```python
@dataclass
class RateLimits:
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    tokens_per_minute: int
    tokens_per_hour: int
    tokens_per_day: int
    current_usage: Dict[str, int]
    reset_time: Optional[datetime]
    error_rate_limit: Optional[int]
```

### RateLimitLog

Represents a rate limit log entry.

```python
@dataclass
class RateLimitLog:
    timestamp: datetime
    endpoint: str
    status_code: int
    response_time: float
    tokens_used: int
    error_type: Optional[str]
```

## Error Handling

The Account Management API raises specific exceptions:

```python
from venice_sdk.errors import APIKeyError, BillingError, UnauthorizedError

try:
    keys = api_keys.list()
except UnauthorizedError:
    print("Admin API key required for this operation")
except APIKeyError as e:
    print(f"API key error: {e}")
except BillingError as e:
    print(f"Billing error: {e}")
```

## Examples

### Complete Account Management Workflow

```python
from venice_sdk import VeniceClient

client = VeniceClient()

# List existing API keys
print("Existing API keys:")
keys = client.api_keys.list()
for key in keys:
    print(f"- {key.name} ({key.id})")

# Create a new API key
new_key = client.api_keys.create(
    name="My New Key",
    permissions=["read", "write"]
)
print(f"Created new key: {new_key.id}")

# Get usage information
usage = client.billing.get_usage()
print(f"Total usage: {usage.total_usage}")
print(f"Credits remaining: {usage.credits_remaining}")

# Check rate limits
limits = client.api_keys.get_rate_limits()
print(f"Rate limits: {limits.requests_per_minute} req/min")

# Get account summary
summary = client.account.get_account_summary()
print(f"Account summary: {summary}")

# Clean up - delete the test key
client.api_keys.delete(new_key.id)
print("Test key deleted")
```

### Admin vs Inference Key Usage

```python
from venice_sdk import VeniceClient

# Using admin key
admin_client = VeniceClient(api_key="admin-key-here")

# Can access all account features
admin_keys = admin_client.api_keys.list()
admin_usage = admin_client.billing.get_usage()
admin_limits = admin_client.api_keys.get_rate_limits()

# Using inference-only key
inference_client = VeniceClient(api_key="inference-key-here")

# Can only access basic features
try:
    inference_keys = inference_client.api_keys.list()
except UnauthorizedError:
    print("Admin permissions required for API key management")

# Basic usage still works
response = inference_client.chat.complete(
    messages=[{"role": "user", "content": "Hello!"}],
    model="llama-3.3-70b"
)
```

## Best Practices

1. **Use Admin Keys Carefully**: Admin keys have full access to your account
2. **Monitor Usage**: Regularly check usage and rate limits
3. **Key Rotation**: Periodically rotate API keys for security
4. **Error Handling**: Always handle potential errors gracefully
5. **Rate Limiting**: Respect rate limits to avoid service interruption
6. **Cost Management**: Monitor usage to control costs

## Troubleshooting

### Common Issues

**"Admin API key required"**
- Ensure you're using an admin API key for account management operations
- Check that your key has the correct permissions

**"Rate limit exceeded"**
- Wait for the rate limit to reset
- Consider implementing exponential backoff
- Check your usage patterns

**"API key not found"**
- Verify the key ID is correct
- Ensure the key hasn't been deleted
- Check that you have permission to access the key

**"Invalid response format"**
- This usually indicates an API change
- Check the SDK version and update if necessary
- Report the issue if it persists
