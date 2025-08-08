"""
HTTP Client for inter-service communication.
Provides a robust HTTP client with retry logic, circuit breaker pattern,
and comprehensive error handling for microservice communication.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientTimeout, ClientSession
from aiohttp.client_exceptions import (
    ClientError, ClientConnectorError, ClientResponseError,
    ServerTimeoutError, ClientPayloadError
)

logger = logging.getLogger(__name__)


class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable."""
    pass


class ServiceTimeoutError(Exception):
    """Raised when a service request times out."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        return False
    
    def on_success(self):
        """Handle successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Handle failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ServiceHTTPClient:
    """HTTP client for inter-service communication."""
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker: Optional[CircuitBreaker] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        timeout = ClientTimeout(total=self.timeout)
        self.session = ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_url(self, endpoint: str) -> str:
        """Get full URL for endpoint."""
        return f"{self.base_url}{endpoint}"
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic and circuit breaker."""
        
        if not self.circuit_breaker.can_execute():
            raise ServiceUnavailableError(f"Service {self.base_url} is unavailable")
        
        url = self._get_url(endpoint)
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "LMS-Service-Client/1.0"
        }
        if headers:
            request_headers.update(headers)
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=request_headers,
                    params=params
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    self.circuit_breaker.on_success()
                    return result
                    
            except ClientResponseError as e:
                logger.error(f"HTTP {method} {url} failed with status {e.status}: {e.message}")
                self.circuit_breaker.on_failure()
                
                if e.status >= 500:  # Server error
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    else:
                        raise ServiceUnavailableError(f"Service {self.base_url} returned {e.status}")
                else:  # Client error
                    raise e
                    
            except (ClientConnectorError, ServerTimeoutError) as e:
                logger.error(f"Connection error for {method} {url}: {e}")
                self.circuit_breaker.on_failure()
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise ServiceUnavailableError(f"Service {self.base_url} is unreachable")
                    
            except ClientError as e:
                logger.error(f"Client error for {method} {url}: {e}")
                self.circuit_breaker.on_failure()
                raise ServiceUnavailableError(f"Service {self.base_url} communication failed")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def patch(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PATCH request."""
        return await self._make_request("PATCH", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._make_request("DELETE", endpoint)


class ServiceRegistry:
    """Service registry for managing service endpoints."""
    
    def __init__(self):
        self.services: Dict[str, str] = {}
        self.clients: Dict[str, ServiceHTTPClient] = {}
    
    def register_service(self, name: str, base_url: str):
        """Register a service with its base URL."""
        self.services[name] = base_url
        self.clients[name] = ServiceHTTPClient(base_url)
    
    def get_client(self, service_name: str) -> ServiceHTTPClient:
        """Get HTTP client for a service."""
        if service_name not in self.clients:
            raise ValueError(f"Service '{service_name}' not registered")
        return self.clients[service_name]
    
    def get_service_url(self, service_name: str) -> str:
        """Get base URL for a service."""
        if service_name not in self.services:
            raise ValueError(f"Service '{service_name}' not registered")
        return self.services[service_name]


# Global service registry
service_registry = ServiceRegistry()


def register_services():
    """Register all services with their URLs."""
    # Development URLs
    service_registry.register_service("user", "http://localhost:8006")
    service_registry.register_service("course", "http://localhost:8000")
    service_registry.register_service("enrollment", "http://localhost:8002")
    service_registry.register_service("assessment", "http://localhost:8003")
    service_registry.register_service("progress", "http://localhost:8004")
    service_registry.register_service("communication", "http://localhost:8005")


# Initialize service registry
register_services()


class ServiceClient:
    """High-level service client for easy inter-service communication."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.client = service_registry.get_client(service_name)
    
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user information from user service."""
        if self.service_name != "user":
            client = service_registry.get_client("user")
            return await client.get(f"/api/v1/users/{user_id}")
        raise ValueError("Cannot call get_user from user service")
    
    async def get_course(self, course_id: int) -> Dict[str, Any]:
        """Get course information from course service."""
        if self.service_name != "course":
            client = service_registry.get_client("course")
            return await client.get(f"/api/v1/courses/{course_id}")
        raise ValueError("Cannot call get_course from course service")
    
    async def get_enrollment(self, enrollment_id: int) -> Dict[str, Any]:
        """Get enrollment information from enrollment service."""
        if self.service_name != "enrollment":
            client = service_registry.get_client("enrollment")
            return await client.get(f"/api/v1/enrollments/{enrollment_id}")
        raise ValueError("Cannot call get_enrollment from enrollment service")
    
    async def get_assessment(self, assessment_id: int) -> Dict[str, Any]:
        """Get assessment information from assessment service."""
        if self.service_name != "assessment":
            client = service_registry.get_client("assessment")
            return await client.get(f"/api/v1/assessments/{assessment_id}")
        raise ValueError("Cannot call get_assessment from assessment service")
    
    async def get_progress(self, progress_id: int) -> Dict[str, Any]:
        """Get progress information from progress service."""
        if self.service_name != "progress":
            client = service_registry.get_client("progress")
            return await client.get(f"/api/v1/progress/{progress_id}")
        raise ValueError("Cannot call get_progress from progress service")
    
    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification in communication service."""
        if self.service_name != "communication":
            client = service_registry.get_client("communication")
            return await client.post("/api/v1/notifications", data=notification_data)
        raise ValueError("Cannot call create_notification from communication service")
    
    async def send_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message through communication service."""
        if self.service_name != "communication":
            client = service_registry.get_client("communication")
            return await client.post("/api/v1/messages", data=message_data)
        raise ValueError("Cannot call send_message from communication service") 