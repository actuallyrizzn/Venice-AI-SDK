"""
Venice AI SDK - Account Management Module

This module provides API key management, rate limiting, and billing capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .client import HTTPClient
from .errors import VeniceAPIError, BillingError, APIKeyError
from .config import load_config


@dataclass
class APIKey:
    """Represents an API key."""
    id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    is_active: bool = True
    permissions: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, Any]] = None


@dataclass
class Web3APIKey:
    """Represents a Web3-compatible API key."""
    id: str
    api_key: str
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    wallet_address: Optional[str] = None
    network: Optional[str] = None


@dataclass
class RateLimits:
    """Represents current rate limit information."""
    requests_per_minute: int
    requests_per_day: int
    tokens_per_minute: int
    tokens_per_day: int
    current_usage: Dict[str, int]
    reset_time: Optional[datetime] = None
    error_rate_limit: Optional[int] = None


@dataclass
class RateLimitLog:
    """Represents a rate limit log entry."""
    timestamp: datetime
    endpoint: str
    status_code: int
    response_time: float
    tokens_used: int
    error_type: Optional[str] = None


@dataclass
class UsageInfo:
    """Represents account usage information."""
    total_usage: int
    current_period: str
    credits_remaining: int
    usage_by_model: Dict[str, Dict[str, int]]
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None


@dataclass
class ModelUsage:
    """Represents usage for a specific model."""
    model_id: str
    requests: int
    tokens: int
    cost: float
    last_used: Optional[datetime] = None


class APIKeysAPI:
    """API key management API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def list(self) -> List[APIKey]:
        """
        List all API keys for the account.
        
        Returns:
            List of APIKey objects
        """
        response = self.client.get("/api_keys")
        result = response.json()
        
        if "data" not in result:
            raise APIKeyError("Invalid response format from API keys endpoint")
        
        keys = []
        for item in result["data"]:
            keys.append(self._parse_api_key(item))
        
        return keys
    
    def generate_web3_key(
        self,
        name: str,
        description: Optional[str] = None,
        wallet_address: Optional[str] = None,
        network: Optional[str] = None,
        **kwargs
    ) -> Web3APIKey:
        """
        Generate a new Web3-compatible API key.
        
        Args:
            name: Name for the API key
            description: Optional description
            wallet_address: Wallet address for Web3 integration
            network: Blockchain network (e.g., "ethereum", "polygon")
            **kwargs: Additional parameters
            
        Returns:
            Web3APIKey object with the new key
        """
        data = {
            "name": name,
            **kwargs
        }
        
        if description:
            data["description"] = description
        if wallet_address:
            data["wallet_address"] = wallet_address
        if network:
            data["network"] = network
        
        response = self.client.post("/api_keys/generate_web3_key", data=data)
        result = response.json()
        
        if "data" not in result:
            raise APIKeyError("Invalid response format from Web3 key generation")
        
        item = result["data"]
        return Web3APIKey(
            id=item["id"],
            api_key=item["api_key"],
            name=item["name"],
            description=item.get("description"),
            created_at=item.get("created_at"),
            wallet_address=item.get("wallet_address"),
            network=item.get("network")
        )
    
    def get_rate_limits(self) -> RateLimits:
        """
        Get current rate limit information.
        
        Returns:
            RateLimits object with current limits and usage
        """
        response = self.client.get("/api_keys/rate_limits")
        result = response.json()
        
        if "data" not in result:
            raise APIKeyError("Invalid response format from rate limits endpoint")
        
        data = result["data"]
        return RateLimits(
            requests_per_minute=data.get("requests_per_minute", 0),
            requests_per_day=data.get("requests_per_day", 0),
            tokens_per_minute=data.get("tokens_per_minute", 0),
            tokens_per_day=data.get("tokens_per_day", 0),
            current_usage=data.get("current_usage", {}),
            reset_time=self._parse_datetime(data.get("reset_time")),
            error_rate_limit=data.get("error_rate_limit")
        )
    
    def get_rate_limits_log(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> List[RateLimitLog]:
        """
        Get rate limit usage log.
        
        Args:
            limit: Maximum number of log entries to return
            offset: Number of log entries to skip
            start_date: Start date for log filtering
            end_date: End date for log filtering
            **kwargs: Additional parameters
            
        Returns:
            List of RateLimitLog objects
        """
        params = {}
        
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        params.update(kwargs)
        
        response = self.client.get("/api_keys/rate_limits/log", params=params)
        result = response.json()
        
        if "data" not in result:
            raise APIKeyError("Invalid response format from rate limits log endpoint")
        
        logs = []
        for item in result["data"]:
            logs.append(self._parse_rate_limit_log(item))
        
        return logs
    
    def _parse_api_key(self, data: Dict[str, Any]) -> APIKey:
        """Parse API key data from response."""
        return APIKey(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=data.get("created_at"),
            last_used=data.get("last_used"),
            is_active=data.get("is_active", True),
            permissions=data.get("permissions"),
            rate_limits=data.get("rate_limits")
        )
    
    def _parse_rate_limit_log(self, data: Dict[str, Any]) -> RateLimitLog:
        """Parse rate limit log entry from response."""
        return RateLimitLog(
            timestamp=self._parse_datetime(data["timestamp"]),
            endpoint=data["endpoint"],
            status_code=data["status_code"],
            response_time=data["response_time"],
            tokens_used=data.get("tokens_used", 0),
            error_type=data.get("error_type")
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common formats
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None


class BillingAPI:
    """Billing and usage API client."""
    
    def __init__(self, client: HTTPClient):
        self.client = client
    
    def get_usage(self) -> UsageInfo:
        """
        Get current account usage information.
        
        Returns:
            UsageInfo object with usage details
        """
        response = self.client.get("/billing/usage")
        result = response.json()
        
        if "data" not in result:
            raise BillingError("Invalid response format from billing endpoint")
        
        data = result["data"]
        return UsageInfo(
            total_usage=data.get("total_usage", 0),
            current_period=data.get("current_period", ""),
            credits_remaining=data.get("credits_remaining", 0),
            usage_by_model=data.get("usage_by_model", {}),
            billing_period_start=self._parse_datetime(data.get("billing_period_start")),
            billing_period_end=self._parse_datetime(data.get("billing_period_end"))
        )
    
    def get_usage_by_model(self) -> Dict[str, ModelUsage]:
        """
        Get usage information broken down by model.
        
        Returns:
            Dictionary mapping model IDs to ModelUsage objects
        """
        usage_info = self.get_usage()
        model_usage = {}
        
        for model_id, usage_data in usage_info.usage_by_model.items():
            model_usage[model_id] = ModelUsage(
                model_id=model_id,
                requests=usage_data.get("requests", 0),
                tokens=usage_data.get("tokens", 0),
                cost=usage_data.get("cost", 0.0),
                last_used=self._parse_datetime(usage_data.get("last_used"))
            )
        
        return model_usage
    
    def get_credits_remaining(self) -> int:
        """
        Get remaining credits for the account.
        
        Returns:
            Number of credits remaining
        """
        usage_info = self.get_usage()
        return usage_info.credits_remaining
    
    def get_total_usage(self) -> int:
        """
        Get total usage for the current period.
        
        Returns:
            Total usage count
        """
        usage_info = self.get_usage()
        return usage_info.total_usage
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None


class AccountManager:
    """High-level account management utilities."""
    
    def __init__(self, api_keys_api: APIKeysAPI, billing_api: BillingAPI):
        self.api_keys_api = api_keys_api
        self.billing_api = billing_api
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive account summary.
        
        Returns:
            Dictionary with account summary information
        """
        try:
            usage_info = self.billing_api.get_usage()
            rate_limits = self.api_keys_api.get_rate_limits()
            api_keys = self.api_keys_api.list()
            
            return {
                "usage": {
                    "total_usage": usage_info.total_usage,
                    "credits_remaining": usage_info.credits_remaining,
                    "current_period": usage_info.current_period
                },
                "rate_limits": {
                    "requests_per_minute": rate_limits.requests_per_minute,
                    "requests_per_day": rate_limits.requests_per_day,
                    "tokens_per_minute": rate_limits.tokens_per_minute,
                    "tokens_per_day": rate_limits.tokens_per_day
                },
                "api_keys": {
                    "total_keys": len(api_keys),
                    "active_keys": len([k for k in api_keys if k.is_active])
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_rate_limit_status(self) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Returns:
            Dictionary with rate limit status information
        """
        try:
            rate_limits = self.api_keys_api.get_rate_limits()
            current_usage = rate_limits.current_usage
            
            return {
                "limits": {
                    "requests_per_minute": rate_limits.requests_per_minute,
                    "requests_per_day": rate_limits.requests_per_day,
                    "tokens_per_minute": rate_limits.tokens_per_minute,
                    "tokens_per_day": rate_limits.tokens_per_day
                },
                "current_usage": current_usage,
                "reset_time": rate_limits.reset_time.isoformat() if rate_limits.reset_time else None,
                "status": "ok" if self._is_within_limits(rate_limits) else "near_limit"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def _is_within_limits(self, rate_limits: RateLimits) -> bool:
        """Check if current usage is within rate limits."""
        current = rate_limits.current_usage
        
        # Check if any limits are exceeded or near limit (>= 90%)
        if (current.get("requests_per_minute", 0) >= rate_limits.requests_per_minute * 0.9 or
            current.get("requests_per_day", 0) >= rate_limits.requests_per_day * 0.9 or
            current.get("tokens_per_minute", 0) >= rate_limits.tokens_per_minute * 0.9 or
            current.get("tokens_per_day", 0) >= rate_limits.tokens_per_day * 0.9):
            return False
        
        return True


# Convenience functions
def get_account_usage(client: Optional[HTTPClient] = None) -> UsageInfo:
    """Convenience function to get account usage."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = BillingAPI(client)
    return api.get_usage()


def get_rate_limits(client: Optional[HTTPClient] = None) -> RateLimits:
    """Convenience function to get rate limits."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = APIKeysAPI(client)
    return api.get_rate_limits()


def list_api_keys(client: Optional[HTTPClient] = None) -> List[APIKey]:
    """Convenience function to list API keys."""
    if client is None:
        from .config import load_config
        from .venice_client import VeniceClient
        config = load_config()
        client = VeniceClient(config)
    
    api = APIKeysAPI(client)
    return api.list()
