"""
Rate limiting metrics and analytics for the Venice SDK.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union


@dataclass
class RateLimitEvent:
    """Rate limit event data."""
    timestamp: datetime
    endpoint: str
    status_code: int
    retry_after: Optional[int] = None
    request_count: int = 1
    remaining_requests: Optional[int] = None
    method: str = "UNKNOWN"


class RateLimitMetrics:
    """Collects and analyzes rate limiting metrics."""

    def __init__(self):
        """Initialize the metrics collector."""
        self.events: List[RateLimitEvent] = []
        self.usage_stats: Dict[str, int] = {}
        self.endpoint_stats: Dict[str, Dict[str, int]] = {}

    def record_rate_limit(
        self,
        endpoint: str,
        status_code: int,
        retry_after: Optional[int] = None,
        request_count: int = 1,
        remaining_requests: Optional[int] = None,
        method: str = "UNKNOWN"
    ) -> None:
        """
        Record a rate limit event.
        
        Args:
            endpoint: API endpoint that was rate limited
            status_code: HTTP status code (typically 429)
            retry_after: Number of seconds to wait before retrying
            request_count: Number of requests in this event
            remaining_requests: Number of remaining requests (if available)
            method: HTTP method (GET, POST, etc.)
        """
        event = RateLimitEvent(
            timestamp=datetime.now(),
            endpoint=endpoint,
            status_code=status_code,
            retry_after=retry_after,
            request_count=request_count,
            remaining_requests=remaining_requests,
            method=method
        )
        self.events.append(event)

        # Update usage stats
        self.usage_stats[endpoint] = self.usage_stats.get(endpoint, 0) + request_count

        # Update endpoint-specific stats
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "total_events": 0,
                "total_requests": 0,
                "total_retry_after": 0,
                "retry_after_count": 0
            }
        
        self.endpoint_stats[endpoint]["total_events"] += 1
        self.endpoint_stats[endpoint]["total_requests"] += request_count
        if retry_after is not None:
            self.endpoint_stats[endpoint]["total_retry_after"] += retry_after
            self.endpoint_stats[endpoint]["retry_after_count"] += 1

    def get_usage_stats(self) -> Dict[str, int]:
        """
        Get usage statistics by endpoint.
        
        Returns:
            Dictionary mapping endpoint to total request count
        """
        return self.usage_stats.copy()

    def get_rate_limit_events(self, endpoint: Optional[str] = None) -> List[RateLimitEvent]:
        """
        Get all rate limit events, optionally filtered by endpoint.
        
        Args:
            endpoint: Optional endpoint to filter by
            
        Returns:
            List of rate limit events
        """
        if endpoint is None:
            return self.events.copy()
        return [event for event in self.events if event.endpoint == endpoint]

    def get_rate_limit_summary(self) -> Dict[str, any]:
        """
        Get summary of rate limiting events.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.events:
            return {
                "total_events": 0,
                "endpoints_affected": 0,
                "total_requests": 0,
                "average_retry_after": None
            }

        endpoints_affected = len(set(event.endpoint for event in self.events))
        total_requests = sum(event.request_count for event in self.events)
        
        retry_after_values = [
            event.retry_after for event in self.events
            if event.retry_after is not None
        ]
        average_retry_after = (
            sum(retry_after_values) / len(retry_after_values)
            if retry_after_values else None
        )

        return {
            "total_events": len(self.events),
            "endpoints_affected": endpoints_affected,
            "total_requests": total_requests,
            "average_retry_after": average_retry_after,
            "endpoints": list(self.endpoint_stats.keys())
        }

    def get_endpoint_summary(self, endpoint: str) -> Optional[Dict[str, any]]:
        """
        Get summary statistics for a specific endpoint.
        
        Args:
            endpoint: Endpoint to get statistics for
            
        Returns:
            Dictionary with endpoint statistics or None if endpoint not found
        """
        if endpoint not in self.endpoint_stats:
            return None

        stats = self.endpoint_stats[endpoint]
        endpoint_events = [e for e in self.events if e.endpoint == endpoint]
        
        retry_after_values = [
            e.retry_after for e in endpoint_events
            if e.retry_after is not None
        ]
        average_retry_after = (
            sum(retry_after_values) / len(retry_after_values)
            if retry_after_values else None
        )

        return {
            "endpoint": endpoint,
            "total_events": stats["total_events"],
            "total_requests": stats["total_requests"],
            "average_retry_after": average_retry_after,
            "methods": list(set(e.method for e in endpoint_events))
        }

    def clear(self) -> None:
        """Clear all collected metrics."""
        self.events.clear()
        self.usage_stats.clear()
        self.endpoint_stats.clear()

    def export_events(self, format: str = "dict") -> Union[List[Dict], str]:
        """
        Export events in the specified format.
        
        Args:
            format: Export format - "dict" (default) or "json"
            
        Returns:
            Events in the specified format
        """
        events_dict = [
            {
                "timestamp": event.timestamp.isoformat(),
                "endpoint": event.endpoint,
                "status_code": event.status_code,
                "retry_after": event.retry_after,
                "request_count": event.request_count,
                "remaining_requests": event.remaining_requests,
                "method": event.method
            }
            for event in self.events
        ]
        
        if format == "json":
            import json
            return json.dumps(events_dict, indent=2)
        return events_dict

