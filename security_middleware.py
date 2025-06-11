"""
Security Middleware for Lekhok/KarigorAI

This module provides security enhancements including:
- Rate limiting
- Security headers
- Request validation
- Brute force protection
"""

import time
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available - using in-memory rate limiting for development")
import hashlib
from fastapi import Request, HTTPException
from fastapi.responses import Response
from typing import Dict, Optional
import logging
import os
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InMemoryRateLimiter:
    """In-memory rate limiter for development (use Redis in production)"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}
    
    def is_rate_limited(self, identifier: str, max_requests: int, window_seconds: int) -> bool:
        """Check if an identifier is rate limited"""
        now = time.time()
        
        # Check if IP is temporarily blocked
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                return True
            else:
                del self.blocked_ips[identifier]
        
        # Clean old requests
        requests = self.requests[identifier]
        while requests and requests[0] < now - window_seconds:
            requests.popleft()
        
        # Check rate limit
        if len(requests) >= max_requests:
            # Block IP for 15 minutes on rate limit exceeded
            self.blocked_ips[identifier] = now + 900  # 15 minutes
            return True
        
        # Add current request
        requests.append(now)
        return False
    
    def get_remaining_requests(self, identifier: str, max_requests: int, window_seconds: int) -> int:
        """Get remaining requests for an identifier"""
        now = time.time()
        requests = self.requests[identifier]
        
        # Clean old requests
        while requests and requests[0] < now - window_seconds:
            requests.popleft()
        
        return max(0, max_requests - len(requests))

# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()

class SecurityMiddleware:
    """Security middleware for authentication and general requests"""
    
    # Rate limiting configurations
    RATE_LIMITS = {
        'auth': {
            'login': {'max_requests': 5, 'window_seconds': 300},  # 5 attempts per 5 minutes
            'register': {'max_requests': 3, 'window_seconds': 300},  # 3 registrations per 5 minutes
            'forgot_password': {'max_requests': 3, 'window_seconds': 300},  # 3 requests per 5 minutes
            'reset_password': {'max_requests': 5, 'window_seconds': 300},  # 5 attempts per 5 minutes
        },
        'general': {
            'api': {'max_requests': 100, 'window_seconds': 60},  # 100 requests per minute
            'story_generation': {'max_requests': 20, 'window_seconds': 300},  # 20 stories per 5 minutes
        }
    }
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (behind proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        
        return 'unknown'
    
    @staticmethod
    def apply_security_headers(response: Response) -> Response:
        """Apply security headers to response"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy (basic)
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
        response.headers['Content-Security-Policy'] = csp
        
        # Only add HSTS in production with HTTPS
        if os.getenv('ENVIRONMENT') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response
    
    @staticmethod
    def check_rate_limit(request: Request, endpoint_type: str, action: str) -> Optional[HTTPException]:
        """Check rate limit for a specific endpoint"""
        client_ip = SecurityMiddleware.get_client_ip(request)
        
        # Get rate limit config
        if endpoint_type in SecurityMiddleware.RATE_LIMITS:
            config = SecurityMiddleware.RATE_LIMITS[endpoint_type].get(action)
            if not config:
                return None
            
            identifier = f"{client_ip}:{endpoint_type}:{action}"
            
            if rate_limiter.is_rate_limited(
                identifier, 
                config['max_requests'], 
                config['window_seconds']
            ):
                remaining_time = 900  # 15 minutes block
                logger.warning(f"Rate limit exceeded for {client_ip} on {endpoint_type}:{action}")
                
                return HTTPException(
                    status_code=429,
                    detail=f"Too many {action} attempts. Please try again in {remaining_time // 60} minutes.",
                    headers={"Retry-After": str(remaining_time)}
                )
        
        return None
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, any]:
        """Validate password strength"""
        errors = []
        score = 0
        
        if len(password) < 6:
            errors.append("Password must be at least 6 characters long")
        elif len(password) >= 8:
            score += 1
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            errors.append("Password should contain at least one uppercase letter")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            errors.append("Password should contain at least one lowercase letter")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            errors.append("Password should contain at least one number")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        
        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 2:
            strength = "medium"
        
        return {
            "valid": len(errors) == 0 or len(password) >= 6,  # Allow if at least 6 chars
            "strength": strength,
            "score": score,
            "errors": errors
        }
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Basic input sanitization"""
        if not text:
            return ""
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove or escape potentially dangerous characters
        # This is basic - in production, use a proper HTML sanitizer
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            text = text.replace(char, '')
        
        return text
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict, ip_address: str = None):
        """Log security events for monitoring"""
        log_entry = {
            "event": event_type,
            "timestamp": time.time(),
            "ip_address": ip_address,
            "details": details
        }
        
        logger.warning(f"SECURITY EVENT: {event_type} from {ip_address} - {details}")
        
        # In production, send to security monitoring system
        # Example: send to SIEM, Slack, email alerts, etc.

# Decorator for rate limiting specific endpoints
def rate_limit(endpoint_type: str, action: str):
    """Decorator to apply rate limiting to endpoints"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Check rate limit
            rate_limit_error = SecurityMiddleware.check_rate_limit(request, endpoint_type, action)
            if rate_limit_error:
                raise rate_limit_error
            
            # Call the original function
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator

# Function to cleanup rate limiter memory periodically
def cleanup_rate_limiter():
    """Clean up old rate limiter data"""
    now = time.time()
    
    # Clean up old request records (older than 1 hour)
    for identifier in list(rate_limiter.requests.keys()):
        requests = rate_limiter.requests[identifier]
        while requests and requests[0] < now - 3600:  # 1 hour
            requests.popleft()
        
        # Remove empty deques
        if not requests:
            del rate_limiter.requests[identifier]
    
    # Clean up expired blocked IPs
    for ip in list(rate_limiter.blocked_ips.keys()):
        if now >= rate_limiter.blocked_ips[ip]:
            del rate_limiter.blocked_ips[ip]
    
    logger.info("Rate limiter cleanup completed") 