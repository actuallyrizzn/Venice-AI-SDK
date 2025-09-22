"""
Comprehensive unit tests for the account module.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from venice_sdk.account import (
    APIKey, Web3APIKey, RateLimits, RateLimitLog, UsageInfo, ModelUsage,
    APIKeysAPI, BillingAPI, AccountManager,
    get_account_usage, get_rate_limits, list_api_keys
)
from venice_sdk.errors import VeniceAPIError, BillingError, APIKeyError


class TestAPIKeyComprehensive:
    """Comprehensive test suite for APIKey class."""

    def test_api_key_initialization(self):
        """Test APIKey initialization with all parameters."""
        api_key = APIKey(
            id="key-123",
            name="Test Key",
            description="A test API key",
            created_at="2023-01-01T00:00:00Z",
            last_used="2023-01-02T00:00:00Z",
            is_active=True,
            permissions={"read": True, "write": False},
            rate_limits={"requests_per_minute": 100}
        )
        
        assert api_key.id == "key-123"
        assert api_key.name == "Test Key"
        assert api_key.description == "A test API key"
        assert api_key.created_at == "2023-01-01T00:00:00Z"
        assert api_key.last_used == "2023-01-02T00:00:00Z"
        assert api_key.is_active is True
        assert api_key.permissions == {"read": True, "write": False}
        assert api_key.rate_limits == {"requests_per_minute": 100}

    def test_api_key_initialization_with_defaults(self):
        """Test APIKey initialization with default values."""
        api_key = APIKey(id="key-123", name="Test Key")
        
        assert api_key.id == "key-123"
        assert api_key.name == "Test Key"
        assert api_key.description is None
        assert api_key.created_at is None
        assert api_key.last_used is None
        assert api_key.is_active is True
        assert api_key.permissions is None
        assert api_key.rate_limits is None

    def test_api_key_equality(self):
        """Test APIKey equality comparison."""
        key1 = APIKey("key-123", "Test Key", "desc", "2023-01-01", "2023-01-02", True)
        key2 = APIKey("key-123", "Test Key", "desc", "2023-01-01", "2023-01-02", True)
        key3 = APIKey("key-456", "Test Key", "desc", "2023-01-01", "2023-01-02", True)
        
        assert key1 == key2
        assert key1 != key3

    def test_api_key_string_representation(self):
        """Test APIKey string representation."""
        api_key = APIKey("key-123", "Test Key")
        key_str = str(api_key)
        
        assert "APIKey" in key_str
        assert "key-123" in key_str


class TestWeb3APIKeyComprehensive:
    """Comprehensive test suite for Web3APIKey class."""

    def test_web3_api_key_initialization(self):
        """Test Web3APIKey initialization with all parameters."""
        web3_key = Web3APIKey(
            id="web3-key-123",
            api_key="sk-web3-1234567890abcdef",
            name="Web3 Test Key",
            description="A Web3 API key",
            created_at="2023-01-01T00:00:00Z",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            network="ethereum"
        )
        
        assert web3_key.id == "web3-key-123"
        assert web3_key.api_key == "sk-web3-1234567890abcdef"
        assert web3_key.name == "Web3 Test Key"
        assert web3_key.description == "A Web3 API key"
        assert web3_key.created_at == "2023-01-01T00:00:00Z"
        assert web3_key.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert web3_key.network == "ethereum"

    def test_web3_api_key_initialization_with_defaults(self):
        """Test Web3APIKey initialization with default values."""
        web3_key = Web3APIKey(
            id="web3-key-123",
            api_key="sk-web3-1234567890abcdef",
            name="Web3 Test Key"
        )
        
        assert web3_key.id == "web3-key-123"
        assert web3_key.api_key == "sk-web3-1234567890abcdef"
        assert web3_key.name == "Web3 Test Key"
        assert web3_key.description is None
        assert web3_key.created_at is None
        assert web3_key.wallet_address is None
        assert web3_key.network is None


class TestRateLimitsComprehensive:
    """Comprehensive test suite for RateLimits class."""

    def test_rate_limits_initialization(self):
        """Test RateLimits initialization with all parameters."""
        reset_time = datetime(2023, 1, 1, 12, 0, 0)
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={"requests_per_minute": 50, "tokens_per_minute": 25000},
            reset_time=reset_time,
            error_rate_limit=10
        )
        
        assert rate_limits.requests_per_minute == 100
        assert rate_limits.requests_per_day == 10000
        assert rate_limits.tokens_per_minute == 50000
        assert rate_limits.tokens_per_day == 5000000
        assert rate_limits.current_usage == {"requests_per_minute": 50, "tokens_per_minute": 25000}
        assert rate_limits.reset_time == reset_time
        assert rate_limits.error_rate_limit == 10

    def test_rate_limits_initialization_with_defaults(self):
        """Test RateLimits initialization with default values."""
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={}
        )
        
        assert rate_limits.requests_per_minute == 100
        assert rate_limits.requests_per_day == 10000
        assert rate_limits.tokens_per_minute == 50000
        assert rate_limits.tokens_per_day == 5000000
        assert rate_limits.current_usage == {}
        assert rate_limits.reset_time is None
        assert rate_limits.error_rate_limit is None


class TestRateLimitLogComprehensive:
    """Comprehensive test suite for RateLimitLog class."""

    def test_rate_limit_log_initialization(self):
        """Test RateLimitLog initialization with all parameters."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        log = RateLimitLog(
            timestamp=timestamp,
            endpoint="/api/chat/completions",
            status_code=200,
            response_time=1.5,
            tokens_used=100,
            error_type=None
        )
        
        assert log.timestamp == timestamp
        assert log.endpoint == "/api/chat/completions"
        assert log.status_code == 200
        assert log.response_time == 1.5
        assert log.tokens_used == 100
        assert log.error_type is None

    def test_rate_limit_log_initialization_with_error(self):
        """Test RateLimitLog initialization with error type."""
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        log = RateLimitLog(
            timestamp=timestamp,
            endpoint="/api/chat/completions",
            status_code=429,
            response_time=0.1,
            tokens_used=0,
            error_type="rate_limit_exceeded"
        )
        
        assert log.timestamp == timestamp
        assert log.endpoint == "/api/chat/completions"
        assert log.status_code == 429
        assert log.response_time == 0.1
        assert log.tokens_used == 0
        assert log.error_type == "rate_limit_exceeded"


class TestUsageInfoComprehensive:
    """Comprehensive test suite for UsageInfo class."""

    def test_usage_info_initialization(self):
        """Test UsageInfo initialization with all parameters."""
        start_time = datetime(2023, 1, 1, 0, 0, 0)
        end_time = datetime(2023, 1, 31, 23, 59, 59)
        usage_info = UsageInfo(
            total_usage=1000,
            current_period="2023-01",
            credits_remaining=5000,
            usage_by_model={
                "llama-3.3-70b": {"requests": 500, "tokens": 100000, "cost": 10.0},
                "gpt-4": {"requests": 300, "tokens": 50000, "cost": 15.0}
            },
            billing_period_start=start_time,
            billing_period_end=end_time
        )
        
        assert usage_info.total_usage == 1000
        assert usage_info.current_period == "2023-01"
        assert usage_info.credits_remaining == 5000
        assert usage_info.usage_by_model == {
            "llama-3.3-70b": {"requests": 500, "tokens": 100000, "cost": 10.0},
            "gpt-4": {"requests": 300, "tokens": 50000, "cost": 15.0}
        }
        assert usage_info.billing_period_start == start_time
        assert usage_info.billing_period_end == end_time

    def test_usage_info_initialization_with_defaults(self):
        """Test UsageInfo initialization with default values."""
        usage_info = UsageInfo(
            total_usage=1000,
            current_period="2023-01",
            credits_remaining=5000,
            usage_by_model={}
        )
        
        assert usage_info.total_usage == 1000
        assert usage_info.current_period == "2023-01"
        assert usage_info.credits_remaining == 5000
        assert usage_info.usage_by_model == {}
        assert usage_info.billing_period_start is None
        assert usage_info.billing_period_end is None


class TestModelUsageComprehensive:
    """Comprehensive test suite for ModelUsage class."""

    def test_model_usage_initialization(self):
        """Test ModelUsage initialization with all parameters."""
        last_used = datetime(2023, 1, 1, 12, 0, 0)
        model_usage = ModelUsage(
            model_id="llama-3.3-70b",
            requests=100,
            tokens=50000,
            cost=10.0,
            last_used=last_used
        )
        
        assert model_usage.model_id == "llama-3.3-70b"
        assert model_usage.requests == 100
        assert model_usage.tokens == 50000
        assert model_usage.cost == 10.0
        assert model_usage.last_used == last_used

    def test_model_usage_initialization_with_defaults(self):
        """Test ModelUsage initialization with default values."""
        model_usage = ModelUsage(
            model_id="llama-3.3-70b",
            requests=100,
            tokens=50000,
            cost=10.0
        )
        
        assert model_usage.model_id == "llama-3.3-70b"
        assert model_usage.requests == 100
        assert model_usage.tokens == 50000
        assert model_usage.cost == 10.0
        assert model_usage.last_used is None


class TestAPIKeysAPIComprehensive:
    """Comprehensive test suite for APIKeysAPI class."""

    def test_api_keys_api_initialization(self, mock_client):
        """Test APIKeysAPI initialization."""
        api = APIKeysAPI(mock_client)
        assert api.client == mock_client

    def test_list_success(self, mock_client):
        """Test successful API keys listing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "key-1",
                    "description": "Key 1",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "lastUsedAt": "2023-01-02T00:00:00Z",
                    "apiKeyType": "ADMIN",
                    "consumptionLimits": {"requests_per_minute": 100}
                },
                {
                    "id": "key-2",
                    "description": "Key 2",
                    "apiKeyType": "INFERENCE"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        keys = api.list()
        
        assert len(keys) == 2
        assert isinstance(keys[0], APIKey)
        assert keys[0].id == "key-1"
        assert keys[0].name == "Key 1"  # description becomes name
        assert keys[0].is_active is True
        assert keys[1].id == "key-2"
        assert keys[1].is_active is True  # Default to True

    def test_list_invalid_response(self, mock_client):
        """Test API keys listing with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        
        with pytest.raises(APIKeyError, match="Invalid response format from API keys endpoint"):
            api.list()

    def test_generate_web3_key_success(self, mock_client):
        """Test successful Web3 key generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "web3-key-123",
                "api_key": "sk-web3-1234567890abcdef",
                "name": "Web3 Key",
                "description": "A Web3 key",
                "created_at": "2023-01-01T00:00:00Z",
                "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
                "network": "ethereum"
            }
        }
        mock_client.post.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        web3_key = api.generate_web3_key(
            name="Web3 Key",
            description="A Web3 key",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678",
            network="ethereum"
        )
        
        assert isinstance(web3_key, Web3APIKey)
        assert web3_key.id == "web3-key-123"
        assert web3_key.api_key == "sk-web3-1234567890abcdef"
        assert web3_key.name == "Web3 Key"
        assert web3_key.wallet_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert web3_key.network == "ethereum"

    def test_generate_web3_key_minimal_params(self, mock_client):
        """Test Web3 key generation with minimal parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "id": "web3-key-123",
                "api_key": "sk-web3-1234567890abcdef",
                "name": "Web3 Key"
            }
        }
        mock_client.post.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        web3_key = api.generate_web3_key(name="Web3 Key")
        
        assert web3_key.id == "web3-key-123"
        assert web3_key.api_key == "sk-web3-1234567890abcdef"
        assert web3_key.name == "Web3 Key"
        assert web3_key.description is None
        assert web3_key.wallet_address is None
        assert web3_key.network is None

    def test_generate_web3_key_invalid_response(self, mock_client):
        """Test Web3 key generation with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.post.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        
        with pytest.raises(APIKeyError, match="Invalid response format from Web3 key generation"):
            api.generate_web3_key(name="Web3 Key")

    def test_get_rate_limits_success(self, mock_client):
        """Test successful rate limits retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "rateLimits": [
                    {
                        "apiModelId": "test-model",
                        "rateLimits": [
                            {
                                "amount": 100,
                                "type": "RPM"
                            },
                            {
                                "amount": 10000,
                                "type": "RPD"
                            },
                            {
                                "amount": 50000,
                                "type": "TPM"
                            }
                        ]
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        rate_limits = api.get_rate_limits()
        
        assert isinstance(rate_limits, RateLimits)
        assert rate_limits.requests_per_minute == 100
        assert rate_limits.requests_per_day == 10000
        assert rate_limits.tokens_per_minute == 50000
        assert rate_limits.tokens_per_hour == 50000 * 60  # Calculated from TPM
        assert rate_limits.tokens_per_day == 50000 * 60 * 24  # Calculated from TPM
        assert rate_limits.current_usage == {}  # Not available in API response
        assert rate_limits.error_rate_limit is None  # Not available in API response

    def test_get_rate_limits_invalid_response(self, mock_client):
        """Test rate limits retrieval with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        
        with pytest.raises(APIKeyError, match="Invalid response format from rate limits endpoint"):
            api.get_rate_limits()

    def test_get_rate_limits_log_success(self, mock_client):
        """Test successful rate limits log retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "modelId": "test-model",
                    "rateLimitType": "RPM"
                },
                {
                    "timestamp": "2023-01-01T12:01:00Z",
                    "modelId": "test-model",
                    "rateLimitType": "RPD"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        logs = api.get_rate_limits_log()
        
        assert len(logs) == 2
        assert isinstance(logs[0], RateLimitLog)
        assert logs[0].endpoint == "model:test-model"  # Uses modelId
        assert logs[0].status_code == 429  # Rate limit exceeded
        assert logs[1].status_code == 429
        assert logs[1].error_type == "RPD"  # rateLimitType

    def test_get_rate_limits_log_with_params(self, mock_client):
        """Test rate limits log retrieval with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_client.get.return_value = mock_response
        
        api = APIKeysAPI(mock_client)
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        
        logs = api.get_rate_limits_log(
            limit=10,
            offset=5,
            start_date=start_date,
            end_date=end_date,
            custom_param="value"
        )
        
        mock_client.get.assert_called_once_with(
            "/api_keys/rate_limits/log",
            params={
                "limit": 10,
                "offset": 5,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "custom_param": "value"
            }
        )

    def test_parse_datetime_iso_format(self, mock_client):
        """Test datetime parsing with ISO format."""
        api = APIKeysAPI(mock_client)
        
        # Test ISO format with Z
        dt = api._parse_datetime("2023-01-01T12:00:00Z")
        assert dt is not None
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12

    def test_parse_datetime_common_format(self, mock_client):
        """Test datetime parsing with common format."""
        api = APIKeysAPI(mock_client)
        
        # Test common format
        dt = api._parse_datetime("2023-01-01 12:00:00")
        assert dt is not None
        assert dt.year == 2023
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12

    def test_parse_datetime_invalid_format(self, mock_client):
        """Test datetime parsing with invalid format."""
        api = APIKeysAPI(mock_client)
        
        # Test invalid format
        dt = api._parse_datetime("invalid-date")
        assert dt is None

    def test_parse_datetime_none(self, mock_client):
        """Test datetime parsing with None input."""
        api = APIKeysAPI(mock_client)
        
        dt = api._parse_datetime(None)
        assert dt is None


class TestBillingAPIComprehensive:
    """Comprehensive test suite for BillingAPI class."""

    def test_billing_api_initialization(self, mock_client):
        """Test BillingAPI initialization."""
        api = BillingAPI(mock_client)
        assert api.client == mock_client

    def test_get_usage_success(self, mock_client):
        """Test successful usage retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "sku": "llama-3.3-70b-llm-output-mtoken",
                    "pricePerUnitUsd": 2,
                    "units": 0.5,
                    "amount": -1.0,
                    "currency": "VCU",
                    "notes": "API Inference"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = BillingAPI(mock_client)
        usage = api.get_usage()
        
        assert isinstance(usage, UsageInfo)
        assert usage.total_usage == 1000  # Calculated from amount * 1000
        assert usage.current_period == "current"  # Default value
        assert usage.credits_remaining == 0  # Not available in API response
        assert "llama-3.3-70b-llm-output-mtoken" in usage.usage_by_model
        model_usage = usage.usage_by_model["llama-3.3-70b-llm-output-mtoken"]
        assert model_usage["requests"] == 1
        assert model_usage["cost"] == 1.0

    def test_get_usage_invalid_response(self, mock_client):
        """Test usage retrieval with invalid response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}
        mock_client.get.return_value = mock_response
        
        api = BillingAPI(mock_client)
        
        with pytest.raises(BillingError, match="Invalid response format from billing endpoint"):
            api.get_usage()

    def test_get_usage_by_model(self, mock_client):
        """Test usage by model retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "sku": "llama-3.3-70b-llm-output-mtoken",
                    "pricePerUnitUsd": 2,
                    "units": 0.5,
                    "amount": -1.0,
                    "currency": "VCU",
                    "notes": "API Inference"
                },
                {
                    "timestamp": "2023-01-01T12:01:00Z",
                    "sku": "gpt-4-llm-output-mtoken",
                    "pricePerUnitUsd": 3,
                    "units": 0.3,
                    "amount": -0.9,
                    "currency": "VCU",
                    "notes": "API Inference"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = BillingAPI(mock_client)
        model_usage = api.get_usage_by_model()
        
        assert len(model_usage) == 2
        assert "llama-3.3-70b-llm-output-mtoken" in model_usage
        assert "gpt-4-llm-output-mtoken" in model_usage
        
        llama_usage = model_usage["llama-3.3-70b-llm-output-mtoken"]
        assert isinstance(llama_usage, ModelUsage)
        assert llama_usage.model_id == "llama-3.3-70b-llm-output-mtoken"
        assert llama_usage.requests == 1
        assert llama_usage.tokens == 500  # Calculated from units * 1000
        assert llama_usage.cost == 1.0

    def test_get_credits_remaining(self, mock_client):
        """Test credits remaining retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "sku": "test-model-llm-output-mtoken",
                    "pricePerUnitUsd": 2,
                    "units": 0.5,
                    "amount": -1.0,
                    "currency": "VCU",
                    "notes": "API Inference"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = BillingAPI(mock_client)
        credits = api.get_credits_remaining()
        
        assert credits == 0  # Not available in API response

    def test_get_total_usage(self, mock_client):
        """Test total usage retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "sku": "test-model-llm-output-mtoken",
                    "pricePerUnitUsd": 2,
                    "units": 0.5,
                    "amount": -1.0,
                    "currency": "VCU",
                    "notes": "API Inference"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        api = BillingAPI(mock_client)
        total_usage = api.get_total_usage()
        
        assert total_usage == 1000  # Calculated from amount * 1000


class TestAccountManagerComprehensive:
    """Comprehensive test suite for AccountManager class."""

    def test_account_manager_initialization(self, mock_client):
        """Test AccountManager initialization."""
        api_keys_api = APIKeysAPI(mock_client)
        billing_api = BillingAPI(mock_client)
        manager = AccountManager(api_keys_api, billing_api)
        
        assert manager.api_keys_api == api_keys_api
        assert manager.billing_api == billing_api

    def test_get_account_summary_success(self, mock_client):
        """Test successful account summary retrieval."""
        # Mock usage info
        usage_info = UsageInfo(
            total_usage=1000,
            current_period="2023-01",
            credits_remaining=5000,
            usage_by_model={}
        )
        
        # Mock rate limits
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={}
        )
        
        # Mock API keys
        api_keys = [
            APIKey("key-1", "Key 1", is_active=True),
            APIKey("key-2", "Key 2", is_active=False)
        ]
        
        with patch.object(BillingAPI, 'get_usage', return_value=usage_info):
            with patch.object(APIKeysAPI, 'get_rate_limits', return_value=rate_limits):
                with patch.object(APIKeysAPI, 'list', return_value=api_keys):
                    manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
                    summary = manager.get_account_summary()
                    
                    assert "usage" in summary
                    assert "rate_limits" in summary
                    assert "api_keys" in summary
                    assert summary["usage"]["total_usage"] == 1000
                    assert summary["api_keys"]["total_keys"] == 2
                    assert summary["api_keys"]["active_keys"] == 1

    def test_get_account_summary_with_error(self, mock_client):
        """Test account summary retrieval with error."""
        # Test that the method handles exceptions gracefully
        manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
        summary = manager.get_account_summary()
        
        # Should return basic access message when no admin permissions
        assert "status" in summary
        assert summary["status"] == "basic_access"

    def test_check_rate_limit_status_success(self, mock_client):
        """Test successful rate limit status check."""
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={"requests_per_minute": 50, "tokens_per_minute": 25000},
            reset_time=datetime(2023, 1, 1, 12, 0, 0)
        )
        
        with patch.object(APIKeysAPI, 'get_rate_limits', return_value=rate_limits):
            manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
            status = manager.check_rate_limit_status()
            
            assert "limits" in status
            assert "current_usage" in status
            assert "status" in status
            assert status["status"] == "ok"

    def test_check_rate_limit_status_near_limit(self, mock_client):
        """Test rate limit status check when near limit."""
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={"requests_per_minute": 95, "tokens_per_minute": 48000}
        )
        
        with patch.object(APIKeysAPI, 'get_rate_limits', return_value=rate_limits):
            manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
            status = manager.check_rate_limit_status()
            
            assert status["status"] == "near_limit"

    def test_check_rate_limit_status_with_error(self, mock_client):
        """Test rate limit status check with error."""
        # Test that the method handles missing admin permissions gracefully
        manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
        status = manager.check_rate_limit_status()
        
        # Should return unknown status when no admin permissions
        assert "status" in status
        assert status["status"] == "unknown"

    def test_is_within_limits_true(self, mock_client):
        """Test _is_within_limits when within limits."""
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={"requests_per_minute": 50, "tokens_per_minute": 25000}
        )
        
        manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
        assert manager._is_within_limits(rate_limits) is True

    def test_is_within_limits_false(self, mock_client):
        """Test _is_within_limits when limits exceeded."""
        rate_limits = RateLimits(
            requests_per_minute=100,
            requests_per_hour=6000,
            requests_per_day=10000,
            tokens_per_minute=50000,
            tokens_per_hour=3000000,
            tokens_per_day=5000000,
            current_usage={"requests_per_minute": 100, "tokens_per_minute": 50000}
        )
        
        manager = AccountManager(APIKeysAPI(mock_client), BillingAPI(mock_client))
        assert manager._is_within_limits(rate_limits) is False


class TestConvenienceFunctionsComprehensive:
    """Comprehensive test suite for convenience functions."""

    def test_get_account_usage_with_client(self, mock_client):
        """Test get_account_usage with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "timestamp": "2023-01-01T12:00:00Z",
                    "sku": "test-model-llm-output-mtoken",
                    "pricePerUnitUsd": 2,
                    "units": 0.5,
                    "amount": -1.0,
                    "currency": "VCU",
                    "notes": "API Inference"
                }
            ]
        }
        mock_client.get.return_value = mock_response
        
        usage = get_account_usage(client=mock_client)
        
        assert isinstance(usage, UsageInfo)
        assert usage.total_usage == 1000

    def test_get_account_usage_without_client(self):
        """Test get_account_usage without provided client."""
        with patch('venice_sdk.config.load_config') as mock_load_config:
            with patch('venice_sdk.venice_client.VeniceClient') as mock_venice_client:
                mock_config = MagicMock()
                mock_load_config.return_value = mock_config
                
                mock_client = MagicMock()
                mock_venice_client.return_value = mock_client
                
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "data": [
                        {
                            "timestamp": "2023-01-01T12:00:00Z",
                            "sku": "test-model-llm-output-mtoken",
                            "pricePerUnitUsd": 2,
                            "units": 0.5,
                            "amount": -1.0,
                            "currency": "VCU",
                            "notes": "API Inference"
                        }
                    ]
                }
                mock_client.get.return_value = mock_response
                
                usage = get_account_usage()
                
                assert isinstance(usage, UsageInfo)
                assert usage.total_usage == 1000

    def test_get_rate_limits_with_client(self, mock_client):
        """Test get_rate_limits with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "rateLimits": [
                    {
                        "apiModelId": "test-model",
                        "rateLimits": [
                            {
                                "amount": 100,
                                "type": "RPM"
                            },
                            {
                                "amount": 10000,
                                "type": "RPD"
                            },
                            {
                                "amount": 50000,
                                "type": "TPM"
                            }
                        ]
                    }
                ]
            }
        }
        mock_client.get.return_value = mock_response
        
        rate_limits = get_rate_limits(client=mock_client)
        
        assert isinstance(rate_limits, RateLimits)
        assert rate_limits.requests_per_minute == 100

    def test_list_api_keys_with_client(self, mock_client):
        """Test list_api_keys with provided client."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "key-1", "name": "Key 1", "is_active": True}
            ]
        }
        mock_client.get.return_value = mock_response
        
        keys = list_api_keys(client=mock_client)
        
        assert len(keys) == 1
        assert isinstance(keys[0], APIKey)
        assert keys[0].id == "key-1"
