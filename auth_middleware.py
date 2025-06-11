"""
Authentication Middleware and Decorators for KarigorAI

This module provides middleware for session management and decorators
for protecting routes and checking permissions.
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import functools
from auth_models import AuthService

# Security scheme for Bearer token
security = HTTPBearer(auto_error=False)

class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extract session token from various sources
            session_token = self.extract_session_token(request)
            
            if session_token:
                user = AuthService.validate_session(session_token)
                if user:
                    # Add user info to request state
                    request.state.user = user
                    request.state.authenticated = True
                else:
                    request.state.user = None
                    request.state.authenticated = False
            else:
                request.state.user = None
                request.state.authenticated = False
        
        await self.app(scope, receive, send)
    
    def extract_session_token(self, request: Request) -> Optional[str]:
        """Extract session token from request headers or cookies"""
        # Try Authorization header first
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]
        
        # Try session cookie
        session_token = request.cookies.get("session_token")
        if session_token:
            return session_token
        
        # Try custom header
        session_token = request.headers.get("X-Session-Token")
        if session_token:
            return session_token
        
        return None

async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to get the current user from request state"""
    return getattr(request.state, 'user', None)

async def get_current_user_required(request: Request) -> Dict[str, Any]:
    """Dependency to get the current user (required - raises exception if not authenticated)"""
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

def require_auth(func):
    """Decorator to require authentication for a route"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find the request object in args/kwargs
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            # Try to find in kwargs
            request = kwargs.get('request')
        
        if not request:
            raise HTTPException(status_code=500, detail="Request object not found")
        
        user = getattr(request.state, 'user', None)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return await func(*args, **kwargs)
    return wrapper

def require_permission(permission: str):
    """Decorator to require a specific permission for a route"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if not AuthService.has_permission(user['role'], permission):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: str):
    """Decorator to require a specific role for a route"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if user['role'] != role:
                raise HTTPException(status_code=403, detail=f"Role {role} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_roles(roles: list):
    """Decorator to require one of multiple roles for a route"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if user['role'] not in roles:
                raise HTTPException(status_code=403, detail=f"One of roles {roles} required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def log_activity(action: str, resource: str = None, resource_id: str = None):
    """Decorator to automatically log user activity"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the request object in args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Try to find in kwargs
                request = kwargs.get('request')
            
            if request:
                user = getattr(request.state, 'user', None)
                if user:
                    # Get client info
                    ip_address = request.client.host if request.client else None
                    user_agent = request.headers.get('user-agent')
                    
                    # Log the activity
                    AuthService.log_activity(
                        user_id=user['id'],
                        action=action,
                        resource=resource,
                        resource_id=resource_id,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class PermissionChecker:
    """Utility class for checking permissions"""
    
    @staticmethod
    def can_manage_users(user: Dict[str, Any]) -> bool:
        """Check if user can manage other users"""
        return AuthService.has_permission(user['role'], 'user_create_general')
    
    @staticmethod
    def can_manage_characters(user: Dict[str, Any]) -> bool:
        """Check if user can manage characters"""
        return AuthService.has_permission(user['role'], 'character_create')
    
    @staticmethod
    def can_view_analytics(user: Dict[str, Any]) -> bool:
        """Check if user can view system analytics"""
        return AuthService.has_permission(user['role'], 'system_analytics')
    
    @staticmethod
    def is_super_admin(user: Dict[str, Any]) -> bool:
        """Check if user is a super admin"""
        return user['role'] == 'super_admin'
    
    @staticmethod
    def is_organization_user(user: Dict[str, Any]) -> bool:
        """Check if user is an organization user"""
        return user['role'] == 'organization_user'
    
    @staticmethod
    def can_access_resource(user: Dict[str, Any], resource_owner_id: int) -> bool:
        """Check if user can access a resource owned by another user"""
        # Users can always access their own resources
        if user['id'] == resource_owner_id:
            return True
        
        # Super admins can access everything
        if PermissionChecker.is_super_admin(user):
            return True
        
        # Organization users can access resources within their organization
        if PermissionChecker.is_organization_user(user) and user.get('organization_id'):
            # Would need to check if resource owner is in same organization
            # This would require additional database query
            return False
        
        return False 