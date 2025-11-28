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
from ._http import ensure_http_client


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
    requests_per_hour: int
    requests_per_day: int
    tokens_per_minute: int
    tokens_per_hour: int
    tokens_per_day: int
    current_usage: Dict[str, int]
    reset_time: Optional[datetime] = None
    error_rate_limit: Optional[int] = None


@dataclass
class RateLimitLog:
    """Represents a rate limit log entry."""
    timestamp: Optional[datetime]
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
    usage_by_model: Dict[str, Dict[str, Any]]
    billing_period_start: Optional[datetime] = None
    billing_period_end: Optional[datetime] = None
    pagination: Optional[Dict[str, Any]] = None


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
    
    def get(self, key_id: str) -> Optional[APIKey]:
        """
        Get a specific API key by ID.
        
        Args:
            key_id: The ID of the API key to retrieve
            
        Returns:
            APIKey object if found, None otherwise
        """
        try:
            response = self.client.get(f"/api_keys/{key_id}")
            result = response.json()

            if "data" not in result:
                return None
                
            return APIKey(
                id=result["data"]["id"],
                name=result["data"].get("description", "Unknown"),
                created_at=result["data"].get("createdAt"),
                last_used=result["data"].get("lastUsedAt"),
                permissions={"type": result["data"].get("apiKeyType")},
                is_active=result["data"].get("is_active", True)
            )
        except VeniceAPIError as e:
            if "not found" in str(e).lower():
                return None
            raise
        except APIKeyError:
            return None
    
    def create(self, name: str, permissions: Optional[List[str]] = None, expires_in_days: Optional[int] = None) -> APIKey:
        """
        Create a new API key.
        
        Args:
            name: Name for the API key (used as description)
            permissions: Optional list of permissions (not used by API)
            expires_in_days: Optional expiration in days (not used by API)
            
        Returns:
            New APIKey object
        """
        try:
            # Map permissions to API key type
            api_key_type = "ADMIN" if permissions and "admin" in [p.lower() for p in permissions] else "INFERENCE"
            
            data = {
                "apiKeyType": api_key_type,
                "description": name
            }
            
            response = self.client.post("/api_keys", data=data)
            result = response.json()
            
            if "data" not in result:
                raise APIKeyError("Invalid response format from API key creation endpoint")
            
            api_key_data = result["data"]
            return APIKey(
                id=api_key_data["id"],
                name=api_key_data.get("description", name),
                description=api_key_data.get("description"),
                created_at=api_key_data.get("createdAt"),
                last_used=api_key_data.get("lastUsedAt"),
                permissions={"type": api_key_data.get("apiKeyType")},
                is_active=True,
                rate_limits=api_key_data.get("consumptionLimit")
            )
        except Exception as e:
            raise APIKeyError(f"Failed to create API key: {e}")
    
    def delete(self, key_id: str) -> bool:
        """
        Delete an API key.
        
        Args:
            key_id: The ID of the API key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.client.delete("/api_keys", params={"id": key_id})
            result = response.json()
            return bool(result.get("success", False))
        except Exception as e:
            raise APIKeyError(f"Failed to delete API key: {e}")
    
    def update(self, key_id: str, name: Optional[str] = None, permissions: Optional[List[str]] = None) -> Optional[APIKey]:
        """
        Update an API key.
        
        Args:
            key_id: The ID of the API key to update
            name: New name for the API key
            permissions: New permissions for the API key
            
        Returns:
            Updated APIKey object if successful, None otherwise
        """
        # The Venice AI API doesn't support updating API keys via the SDK
        # This is typically done through the web interface
        raise APIKeyError("API key updating is not supported via the SDK. Please use the Venice AI web interface.")
    
    def generate_web3_key(
        self,
        name: str,
        description: Optional[str] = None,
        wallet_address: Optional[str] = None,
        network: Optional[str] = None,
        **kwargs: Any
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
        
        # Parse rate limits from the API response
        # The API returns rateLimits as an array of objects with apiModelId and rateLimits
        rate_limits_data = data.get("rateLimits", [])
        
        # Parse rate limits from the API response structure
        requests_per_minute = 0
        requests_per_hour = 0
        requests_per_day = 0
        tokens_per_minute = 0
        tokens_per_hour = 0
        tokens_per_day = 0
        
        if rate_limits_data and len(rate_limits_data) > 0:
            # Use the first model's rate limits
            first_model = rate_limits_data[0]
            if isinstance(first_model, dict) and "rateLimits" in first_model:
                rate_limits = first_model["rateLimits"]
                for limit in rate_limits:
                    limit_type = limit.get("type", "")
                    amount = limit.get("amount", 0)
                    
                    if limit_type == "RPM":
                        requests_per_minute = amount
                    elif limit_type == "RPD":
                        requests_per_day = amount
                        requests_per_hour = amount // 24  # Estimate hourly from daily
                    elif limit_type == "TPM":
                        tokens_per_minute = amount
                        tokens_per_hour = amount * 60  # Estimate hourly from minute
                        tokens_per_day = amount * 60 * 24  # Estimate daily from minute
        
        return RateLimits(
            requests_per_minute=requests_per_minute,
            requests_per_hour=requests_per_hour,
            requests_per_day=requests_per_day,
            tokens_per_minute=tokens_per_minute,
            tokens_per_hour=tokens_per_hour,
            tokens_per_day=tokens_per_day,
            current_usage={},  # Not available in current API response
            reset_time=self._parse_datetime(data.get("nextEpochBegins")),
            error_rate_limit=None
        )
    
    def get_rate_limits_log(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs: Any
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
        params: Dict[str, Any] = {}
        
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
    
    def get_rate_limit_logs(self, limit: Optional[int] = None) -> List[RateLimitLog]:
        """Alias for get_rate_limits_log() for backward compatibility."""
        return self.get_rate_limits_log(limit)
    
    def _parse_api_key(self, data: Dict[str, Any]) -> APIKey:
        """Parse API key data from response."""
        return APIKey(
            id=data["id"],
            name=data.get("description", "Unknown"),  # API uses description as name
            description=data.get("description"),
            created_at=data.get("createdAt"),
            last_used=data.get("lastUsedAt"),
            is_active=True,  # Assume active if returned
            permissions={"type": data.get("apiKeyType")},  # Store API key type as permission
            rate_limits=data.get("consumptionLimits")
        )
    
    def _parse_rate_limit_log(self, data: Dict[str, Any]) -> RateLimitLog:
        """Parse rate limit log entry from response."""
        return RateLimitLog(
            timestamp=self._parse_datetime(data["timestamp"]),
            endpoint=f"model:{data.get('modelId', 'unknown')}",  # Use modelId as endpoint
            status_code=429,  # Rate limit exceeded
            response_time=0.0,  # Not available in API response
            tokens_used=0,  # Not available in API response
            error_type=data.get("rateLimitType")
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
    
    def get_usage(
        self,
        currency: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 200,
        page: int = 1,
        sort_order: str = "desc"
    ) -> UsageInfo:
        """
        Get current account usage information.
        
        Args:
            currency: Filter by currency (USD, VCU, DIEM)
            start_date: Start date for filtering records (ISO 8601)
            end_date: End date for filtering records (ISO 8601)
            limit: Number of items per page (0-500, default 200)
            page: Page number for pagination (default 1)
            sort_order: Sort order for createdAt field (asc/desc, default desc)
        
        Returns:
            UsageInfo object with usage details
        """
        params: Dict[str, Any] = {}
        
        if currency:
            params["currency"] = currency
        if start_date:
            params["startDate"] = start_date.isoformat()
        if end_date:
            params["endDate"] = end_date.isoformat()
        if limit != 200:
            params["limit"] = limit
        if page != 1:
            params["page"] = page
        if sort_order != "desc":
            params["sortOrder"] = sort_order
        
        response = self.client.get("/billing/usage", params=params)
        result = response.json()
        
        if "data" not in result:
            raise BillingError("Invalid response format from billing endpoint")
        
        data = result["data"]
        pagination = result.get("pagination", {})
        
        if isinstance(data, dict):
            usage_by_model = {}
            raw_usage = data.get("usage_by_model") or {}
            if isinstance(raw_usage, dict):
                for model_id, stats in raw_usage.items():
                    if not isinstance(stats, dict):
                        continue
                    usage_by_model[model_id] = {
                        "requests": int(stats.get("requests", 0)),
                        "tokens": int(stats.get("tokens", 0)),
                        "cost": int(stats.get("cost", 0)),
                    }
            return UsageInfo(
                total_usage=int(data.get("total_usage", 0)),
                current_period=data.get("current_period", "current"),
                credits_remaining=int(data.get("credits_remaining", 0)),
                usage_by_model=usage_by_model,
                billing_period_start=self._parse_datetime(data.get("billing_period_start")),
                billing_period_end=self._parse_datetime(data.get("billing_period_end")),
                pagination=pagination or data.get("pagination"),
            )
        
        # Parse usage data from array of usage entries
        total_usage = 0
        usage_by_model = {}
        
        for entry in data:
            if not isinstance(entry, dict):
                continue
            amount = entry.get("amount", 0)
            total_usage += abs(amount)  # Use absolute value for total usage
            
            sku = entry.get("sku", "unknown")
            if sku not in usage_by_model:
                usage_by_model[sku] = {
                    "requests": 0,
                    "tokens": 0,
                    "cost": 0,
                }
            
            usage_by_model[sku]["cost"] += int(abs(amount))
            # Estimate tokens from units if available
            units = entry.get("units", 0)
            usage_by_model[sku]["tokens"] += int(units * 1000)  # Convert to token estimate
            usage_by_model[sku]["requests"] += 1
        
        return UsageInfo(
            total_usage=int(total_usage * 1000),  # Convert to integer
            current_period="current",  # Not available in API response
            credits_remaining=0,  # Not available in this endpoint
            usage_by_model=usage_by_model,
            billing_period_start=None,  # Not available in API response
            billing_period_end=None,  # Not available in API response
            pagination=pagination
        )
    
    def get_usage_by_model(self) -> Dict[str, ModelUsage]:
        """
        Get usage information broken down by model.
        
        Returns:
            Dictionary mapping model IDs to ModelUsage objects
        """
        usage_info = self.get_usage()
        model_usage: Dict[str, ModelUsage] = {}
        
        for model_id, usage_data in usage_info.usage_by_model.items():
            last_used_raw = usage_data.get("last_used")
            last_used = self._parse_datetime(last_used_raw) if isinstance(last_used_raw, str) else None
            model_usage[model_id] = ModelUsage(
                model_id=model_id,
                requests=int(usage_data.get("requests", 0)),
                tokens=int(usage_data.get("tokens", 0)),
                cost=float(usage_data.get("cost", 0.0)),
                last_used=last_used
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
    
    def get_pagination_info(self) -> Dict[str, Any]:
        """
        Get pagination information for the last usage request.
        
        Returns:
            Dictionary with pagination details (limit, page, total, totalPages)
        """
        usage_info = self.get_usage()
        return usage_info.pagination or {}
    
    def get_total_usage(self) -> int:
        """
        Get total usage for the current period.
        
        Returns:
            Total usage count
        """
        usage_info = self.get_usage()
        return usage_info.total_usage
    
    def get_usage_info(self) -> UsageInfo:
        """Alias for get_usage() for backward compatibility."""
        return self.get_usage()
    
    def get_model_usage(self) -> Dict[str, ModelUsage]:
        """Alias for get_usage_by_model() for backward compatibility."""
        return self.get_usage_by_model()
    
    def get_billing_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive billing summary.
        
        Returns:
            Dictionary with billing summary information
        """
        try:
            response = self.client.get("/billing/summary")
            result = response.json()
            
            if "data" not in result:
                raise BillingError("Invalid response format from billing summary endpoint")
            
            data = result["data"]
            if not isinstance(data, dict):
                raise BillingError("Billing summary payload must be an object")
            return data
        except Exception as e:
            # Fallback to basic usage info if billing summary is not available
            usage_info = self.get_usage()
            return {
                "current_balance": 0,  # Not available
                "total_spent": usage_info.total_usage,
                "last_payment": None,  # Not available
                "next_billing_date": None,  # Not available
                "subscription_status": "active"  # Assume active
            }
    
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
            # Try to get usage info (may require admin permissions)
            usage_info = None
            try:
                usage_info = self.billing_api.get_usage()
            except Exception:
                pass  # Not an admin key, skip usage info
            
            # Try to get rate limits (may require admin permissions)
            rate_limits = None
            try:
                rate_limits = self.api_keys_api.get_rate_limits()
            except Exception:
                pass  # Not an admin key, skip rate limits
            
            # Try to get API keys (may require admin permissions)
            api_keys = []
            try:
                api_keys = self.api_keys_api.list()
            except Exception:
                pass  # Not an admin key, skip API keys
            
            result: Dict[str, Any] = {}
            
            if usage_info:
                result["usage"] = {
                    "total_usage": usage_info.total_usage,
                    "credits_remaining": usage_info.credits_remaining,
                    "current_period": usage_info.current_period
                }
            
            if rate_limits:
                result["rate_limits"] = {
                    "requests_per_minute": rate_limits.requests_per_minute,
                    "requests_per_day": rate_limits.requests_per_day,
                    "tokens_per_minute": rate_limits.tokens_per_minute,
                    "tokens_per_day": rate_limits.tokens_per_day
                }
            
            if api_keys:
                result["api_keys"] = {
                    "total_keys": len(api_keys),
                    "active_keys": len([k for k in api_keys if k.is_active])
                }
            
            # If we couldn't get any admin data, return a basic summary
            if not result:
                result = {
                    "status": "basic_access",
                    "message": "Limited account access - admin permissions required for full summary"
                }
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def check_rate_limit_status(self) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Returns:
            Dictionary with rate limit status information
        """
        try:
            # Try to get rate limits (may require admin permissions)
            rate_limits = None
            try:
                rate_limits = self.api_keys_api.get_rate_limits()
            except Exception:
                pass  # Not an admin key, skip rate limits
            
            if rate_limits:
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
            else:
                # Return basic status if we can't get rate limit info
                return {
                    "status": "unknown",
                    "message": "Rate limit information not available - admin permissions required"
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
    
    def get_rate_limit_logs(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs: Any,
    ) -> List[RateLimitLog]:
        """Proxy to API key rate limit logs for backward compatibility."""
        return self.api_keys_api.get_rate_limits_log(
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )
    
    def get_usage_info(self) -> UsageInfo:
        """Alias for get_usage() for backward compatibility."""
        return self.billing_api.get_usage()
    
    def get_model_usage(self) -> Dict[str, ModelUsage]:
        """Alias for get_usage_by_model() for backward compatibility."""
        return self.billing_api.get_usage_by_model()
    
    def get_billing_summary(self) -> Dict[str, Any]:
        """Proxy to the billing summary endpoint."""
        return self.billing_api.get_billing_summary()


# Convenience functions
def get_account_usage(client: Optional[HTTPClient] = None) -> UsageInfo:
    """Convenience function to get account usage."""
    http_client = ensure_http_client(client)
    api = BillingAPI(http_client)
    return api.get_usage()


def get_rate_limits(client: Optional[HTTPClient] = None) -> RateLimits:
    """Convenience function to get rate limits."""
    http_client = ensure_http_client(client)
    api = APIKeysAPI(http_client)
    return api.get_rate_limits()


def list_api_keys(client: Optional[HTTPClient] = None) -> List[APIKey]:
    """Convenience function to list API keys."""
    http_client = ensure_http_client(client)
    api = APIKeysAPI(http_client)
    return api.list()
