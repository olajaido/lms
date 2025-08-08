"""
Authentication middleware for service-to-service communication.
Provides JWT token validation and service authentication.
"""

import jwt
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT Configuration (should match user service)
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"


class ServiceAuthMiddleware:
    """Middleware for service-to-service authentication."""
    
    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    async def authenticate_service_request(self, request: Request) -> Dict[str, Any]:
        """Authenticate service-to-service request."""
        # Check for service authentication header
        service_token = request.headers.get("X-Service-Token")
        if service_token:
            # Simple service token validation (in production, use proper service tokens)
            if service_token == "service-secret-token":
                return {"service": "internal", "authenticated": True}
        
        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = self.verify_token(token)
            if payload:
                return {
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "role": payload.get("role"),
                    "authenticated": True
                }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    async def require_service_auth(self, request: Request) -> Dict[str, Any]:
        """Require service authentication."""
        return await self.authenticate_service_request(request)
    
    async def require_user_auth(self, request: Request) -> Dict[str, Any]:
        """Require user authentication."""
        auth_info = await self.authenticate_service_request(request)
        if auth_info.get("service") == "internal":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User authentication required"
            )
        return auth_info
    
    async def require_admin_auth(self, request: Request) -> Dict[str, Any]:
        """Require admin authentication."""
        auth_info = await self.require_user_auth(request)
        if auth_info.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return auth_info


# Global middleware instance
service_auth_middleware = ServiceAuthMiddleware()


class ServiceAuthDependency:
    """Dependency for service authentication."""
    
    def __init__(self, require_user: bool = True, require_admin: bool = False):
        self.require_user = require_user
        self.require_admin = require_admin
    
    async def __call__(self, request: Request) -> Dict[str, Any]:
        if self.require_admin:
            return await service_auth_middleware.require_admin_auth(request)
        elif self.require_user:
            return await service_auth_middleware.require_user_auth(request)
        else:
            return await service_auth_middleware.require_service_auth(request)


# Common authentication dependencies
require_service_auth = ServiceAuthDependency(require_user=False)
require_user_auth = ServiceAuthDependency(require_user=True)
require_admin_auth = ServiceAuthDependency(require_user=True, require_admin=True) 