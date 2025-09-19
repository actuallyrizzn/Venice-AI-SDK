"""
Live tests for the Account module.

These tests make real API calls to verify account functionality.
"""

import pytest
import os
from venice_sdk.account import APIKeysAPI, BillingAPI, AccountManager
from venice_sdk.client import HTTPClient
from venice_sdk.config import Config
from venice_sdk.errors import VeniceAPIError


@pytest.mark.live
class TestAccountAPILive:
    """Live tests for Account APIs with real API calls."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.api_key = os.getenv("VENICE_API_KEY")
        if not self.api_key:
            pytest.skip("VENICE_API_KEY environment variable not set")
        
        self.config = Config(api_key=self.api_key)
        self.client = HTTPClient(self.config)
        self.api_keys_api = APIKeysAPI(self.client)
        self.billing_api = BillingAPI(self.client)
        self.account_manager = AccountManager(self.api_keys_api, self.billing_api)

    def test_list_api_keys(self):
        """Test listing API keys."""
        api_keys = self.api_keys_api.list()
        
        assert isinstance(api_keys, list)
        assert len(api_keys) > 0
        
        # Verify API key structure
        api_key = api_keys[0]
        assert hasattr(api_key, 'id')
        assert hasattr(api_key, 'name')
        assert hasattr(api_key, 'created')
        assert hasattr(api_key, 'last_used')
        assert hasattr(api_key, 'permissions')
        assert hasattr(api_key, 'is_active')

    def test_get_api_key_by_id(self):
        """Test getting a specific API key by ID."""
        # First get the list to find a valid API key ID
        api_keys = self.api_keys_api.list()
        assert len(api_keys) > 0
        
        api_key_id = api_keys[0].id
        api_key = self.api_keys_api.get(api_key_id)
        
        assert api_key is not None
        assert api_key.id == api_key_id
        assert hasattr(api_key, 'name')
        assert hasattr(api_key, 'created')

    def test_get_nonexistent_api_key(self):
        """Test getting an API key that doesn't exist."""
        api_key = self.api_keys_api.get("nonexistent-api-key-id")
        assert api_key is None

    def test_create_api_key(self):
        """Test creating a new API key."""
        key_name = f"test-key-{os.getpid()}"
        
        try:
            api_key = self.api_keys_api.create(
                name=key_name,
                permissions=["read", "write"],
                expires_in_days=30
            )
            
            assert api_key is not None
            assert hasattr(api_key, 'id')
            assert hasattr(api_key, 'name')
            assert hasattr(api_key, 'key')
            assert hasattr(api_key, 'created')
            assert api_key.name == key_name
            
            # Clean up - delete the created key
            self.api_keys_api.delete(api_key.id)
            
        except VeniceAPIError as e:
            # API key creation might not be allowed for this account
            if e.status_code == 403:
                pytest.skip("API key creation not allowed for this account")
            raise

    def test_delete_api_key(self):
        """Test deleting an API key."""
        # First create a key to delete
        key_name = f"test-key-to-delete-{os.getpid()}"
        
        try:
            api_key = self.api_keys_api.create(
                name=key_name,
                permissions=["read"],
                expires_in_days=1
            )
            
            # Delete the key
            success = self.api_keys_api.delete(api_key.id)
            assert success is True
            
        except VeniceAPIError as e:
            # API key creation might not be allowed for this account
            if e.status_code == 403:
                pytest.skip("API key creation not allowed for this account")
            raise

    def test_update_api_key(self):
        """Test updating an API key."""
        # First create a key to update
        key_name = f"test-key-to-update-{os.getpid()}"
        
        try:
            api_key = self.api_keys_api.create(
                name=key_name,
                permissions=["read"],
                expires_in_days=30
            )
            
            # Update the key
            updated_key = self.api_keys_api.update(
                api_key.id,
                name=f"{key_name}-updated",
                permissions=["read", "write"]
            )
            
            assert updated_key is not None
            assert updated_key.name == f"{key_name}-updated"
            
            # Clean up - delete the created key
            self.api_keys_api.delete(api_key.id)
            
        except VeniceAPIError as e:
            # API key operations might not be allowed for this account
            if e.status_code == 403:
                pytest.skip("API key operations not allowed for this account")
            raise

    def test_get_rate_limits(self):
        """Test getting rate limits."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits is not None
        assert hasattr(rate_limits, 'requests_per_minute')
        assert hasattr(rate_limits, 'requests_per_hour')
        assert hasattr(rate_limits, 'requests_per_day')
        assert hasattr(rate_limits, 'tokens_per_minute')
        assert hasattr(rate_limits, 'tokens_per_hour')
        assert hasattr(rate_limits, 'tokens_per_day')
        
        # Rate limits should be positive numbers
        assert rate_limits.requests_per_minute > 0
        assert rate_limits.requests_per_hour > 0
        assert rate_limits.requests_per_day > 0

    def test_get_rate_limit_logs(self):
        """Test getting rate limit logs."""
        logs = self.api_keys_api.get_rate_limit_logs()
        
        assert isinstance(logs, list)
        # Logs might be empty if no rate limiting has occurred
        
        if logs:
            log = logs[0]
            assert hasattr(log, 'timestamp')
            assert hasattr(log, 'endpoint')
            assert hasattr(log, 'status_code')
            assert hasattr(log, 'response_time')

    def test_get_usage_info(self):
        """Test getting usage information."""
        usage_info = self.billing_api.get_usage_info()
        
        assert usage_info is not None
        assert hasattr(usage_info, 'total_requests')
        assert hasattr(usage_info, 'total_tokens')
        assert hasattr(usage_info, 'total_cost')
        assert hasattr(usage_info, 'period_start')
        assert hasattr(usage_info, 'period_end')
        assert hasattr(usage_info, 'model_usage')
        
        # Usage should be non-negative
        assert usage_info.total_requests >= 0
        assert usage_info.total_tokens >= 0
        assert usage_info.total_cost >= 0

    def test_get_model_usage(self):
        """Test getting model usage information."""
        model_usage = self.billing_api.get_model_usage()
        
        assert isinstance(model_usage, list)
        
        if model_usage:
            usage = model_usage[0]
            assert hasattr(usage, 'model')
            assert hasattr(usage, 'requests')
            assert hasattr(usage, 'tokens')
            assert hasattr(usage, 'cost')
            
            # Usage should be non-negative
            assert usage.requests >= 0
            assert usage.tokens >= 0
            assert usage.cost >= 0

    def test_get_billing_summary(self):
        """Test getting billing summary."""
        summary = self.billing_api.get_billing_summary()
        
        assert summary is not None
        assert hasattr(summary, 'current_balance')
        assert hasattr(summary, 'total_spent')
        assert hasattr(summary, 'last_payment')
        assert hasattr(summary, 'next_billing_date')
        assert hasattr(summary, 'subscription_status')
        
        # Balance and spending should be non-negative
        assert summary.current_balance >= 0
        assert summary.total_spent >= 0

    def test_account_manager_get_account_summary(self):
        """Test AccountManager get_account_summary method."""
        summary = self.account_manager.get_account_summary()
        
        assert summary is not None
        assert isinstance(summary, dict)
        assert "api_keys" in summary
        assert "billing" in summary
        assert "rate_limits" in summary
        
        # Verify structure
        assert isinstance(summary["api_keys"], list)
        assert isinstance(summary["billing"], dict)
        assert isinstance(summary["rate_limits"], dict)

    def test_account_manager_check_rate_limit_status(self):
        """Test AccountManager check_rate_limit_status method."""
        status = self.account_manager.check_rate_limit_status()
        
        assert status is not None
        assert isinstance(status, dict)
        assert "current_usage" in status
        assert "limits" in status
        assert "status" in status
        
        # Status should be one of the expected values
        assert status["status"] in ["ok", "warning", "critical"]

    def test_api_key_permissions(self):
        """Test API key permissions structure."""
        api_keys = self.api_keys_api.list()
        assert len(api_keys) > 0
        
        api_key = api_keys[0]
        if api_key.permissions:
            assert isinstance(api_key.permissions, list)
            assert all(isinstance(perm, str) for perm in api_key.permissions)
            assert all(len(perm) > 0 for perm in api_key.permissions)

    def test_api_key_creation_timestamps(self):
        """Test API key creation timestamps."""
        api_keys = self.api_keys_api.list()
        assert len(api_keys) > 0
        
        for api_key in api_keys:
            if api_key.created:
                assert isinstance(api_key.created, (int, str))
                if isinstance(api_key.created, int):
                    assert api_key.created > 0

    def test_api_key_last_used_timestamps(self):
        """Test API key last used timestamps."""
        api_keys = self.api_keys_api.list()
        assert len(api_keys) > 0
        
        for api_key in api_keys:
            if api_key.last_used:
                assert isinstance(api_key.last_used, (int, str))
                if isinstance(api_key.last_used, int):
                    assert api_key.last_used > 0

    def test_api_key_active_status(self):
        """Test API key active status."""
        api_keys = self.api_keys_api.list()
        assert len(api_keys) > 0
        
        for api_key in api_keys:
            assert isinstance(api_key.is_active, bool)

    def test_rate_limit_requests_per_minute(self):
        """Test rate limit requests per minute."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.requests_per_minute > 0
        assert isinstance(rate_limits.requests_per_minute, int)

    def test_rate_limit_requests_per_hour(self):
        """Test rate limit requests per hour."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.requests_per_hour > 0
        assert isinstance(rate_limits.requests_per_hour, int)

    def test_rate_limit_requests_per_day(self):
        """Test rate limit requests per day."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.requests_per_day > 0
        assert isinstance(rate_limits.requests_per_day, int)

    def test_rate_limit_tokens_per_minute(self):
        """Test rate limit tokens per minute."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.tokens_per_minute > 0
        assert isinstance(rate_limits.tokens_per_minute, int)

    def test_rate_limit_tokens_per_hour(self):
        """Test rate limit tokens per hour."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.tokens_per_hour > 0
        assert isinstance(rate_limits.tokens_per_hour, int)

    def test_rate_limit_tokens_per_day(self):
        """Test rate limit tokens per day."""
        rate_limits = self.api_keys_api.get_rate_limits()
        
        assert rate_limits.tokens_per_day > 0
        assert isinstance(rate_limits.tokens_per_day, int)

    def test_usage_info_period_dates(self):
        """Test usage info period dates."""
        usage_info = self.billing_api.get_usage_info()
        
        if usage_info.period_start:
            assert isinstance(usage_info.period_start, (int, str))
            if isinstance(usage_info.period_start, int):
                assert usage_info.period_start > 0
        
        if usage_info.period_end:
            assert isinstance(usage_info.period_end, (int, str))
            if isinstance(usage_info.period_end, int):
                assert usage_info.period_end > 0

    def test_model_usage_structure(self):
        """Test model usage structure."""
        model_usage = self.billing_api.get_model_usage()
        
        if model_usage:
            for usage in model_usage:
                assert isinstance(usage.model, str)
                assert len(usage.model) > 0
                assert isinstance(usage.requests, int)
                assert isinstance(usage.tokens, int)
                assert isinstance(usage.cost, (int, float))

    def test_billing_summary_subscription_status(self):
        """Test billing summary subscription status."""
        summary = self.billing_api.get_billing_summary()
        
        if summary.subscription_status:
            assert isinstance(summary.subscription_status, str)
            assert summary.subscription_status in ["active", "inactive", "suspended", "cancelled"]

    def test_billing_summary_payment_dates(self):
        """Test billing summary payment dates."""
        summary = self.billing_api.get_billing_summary()
        
        if summary.last_payment:
            assert isinstance(summary.last_payment, (int, str))
            if isinstance(summary.last_payment, int):
                assert summary.last_payment > 0
        
        if summary.next_billing_date:
            assert isinstance(summary.next_billing_date, (int, str))
            if isinstance(summary.next_billing_date, int):
                assert summary.next_billing_date > 0

    def test_account_error_handling(self):
        """Test error handling in account APIs."""
        # Test with invalid client
        from venice_sdk.client import HTTPClient
        from venice_sdk.config import Config
        
        invalid_config = Config(api_key="invalid-key")
        invalid_client = HTTPClient(invalid_config)
        invalid_api_keys_api = APIKeysAPI(invalid_client)
        
        with pytest.raises(VeniceAPIError):
            invalid_api_keys_api.list()

    def test_account_performance(self):
        """Test account API performance."""
        import time
        
        # Test API keys listing performance
        start_time = time.time()
        api_keys = self.api_keys_api.list()
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert len(api_keys) > 0
        assert response_time < 10  # Should complete within 10 seconds
        assert response_time > 0

    def test_account_concurrent_access(self):
        """Test concurrent access to account APIs."""
        import threading
        import time
        
        results = []
        errors = []
        
        def get_api_keys():
            try:
                api_keys = self.api_keys_api.list()
                results.append(len(api_keys))
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=get_api_keys)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(results) == 3
        assert len(errors) == 0
        assert all(count > 0 for count in results)

    def test_account_memory_usage(self):
        """Test memory usage during account operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform multiple account operations
        for _ in range(10):
            api_keys = self.api_keys_api.list()
            assert len(api_keys) > 0
            
            usage_info = self.billing_api.get_usage_info()
            assert usage_info is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024

    def test_account_data_consistency(self):
        """Test account data consistency across multiple calls."""
        api_keys1 = self.api_keys_api.list()
        api_keys2 = self.api_keys_api.list()
        
        # Data should be consistent
        assert len(api_keys1) == len(api_keys2)
        
        # API key IDs should be the same
        ids1 = [key.id for key in api_keys1]
        ids2 = [key.id for key in api_keys2]
        assert set(ids1) == set(ids2)

    def test_convenience_functions(self):
        """Test convenience functions."""
        from venice_sdk.account import get_account_usage, get_rate_limits, list_api_keys
        
        # Test get_account_usage
        usage = get_account_usage(self.client)
        assert usage is not None
        assert hasattr(usage, 'total_requests')
        assert hasattr(usage, 'total_tokens')
        assert hasattr(usage, 'total_cost')
        
        # Test get_rate_limits
        limits = get_rate_limits(self.client)
        assert limits is not None
        assert hasattr(limits, 'requests_per_minute')
        assert hasattr(limits, 'requests_per_hour')
        assert hasattr(limits, 'requests_per_day')
        
        # Test list_api_keys
        keys = list_api_keys(self.client)
        assert isinstance(keys, list)
        assert len(keys) > 0
