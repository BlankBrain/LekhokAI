"""
Authentication Routes for KarigorAI

This module defines all authentication-related API endpoints including
registration, login, logout, Google OAuth, profile management, and user management.
"""

from fastapi import APIRouter, Request, HTTPException, Depends, Form, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
import secrets
import datetime
from auth_models import AuthService, UserRole, UserStatus, AuthProvider
from auth_middleware import (
    get_current_user, get_current_user_required, require_auth, 
    require_permission, require_role, log_activity, PermissionChecker
)
from google_oauth import GoogleOAuthService
from security_middleware import SecurityMiddleware, rate_limit
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize Google OAuth service
google_oauth = GoogleOAuthService()

# Pydantic models for request/response
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    full_name: str
    organization_name: Optional[str] = None
    privacy_policy_accepted: bool = True
    terms_of_service_accepted: bool = True

class RegisterRequestCompat(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    privacy_policy_accepted: bool = True
    terms_of_service_accepted: bool = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    token: str

class GoogleTokenRequest(BaseModel):
    id_token: str
    privacy_policy_accepted: bool = False
    terms_of_service_accepted: bool = False

class GoogleCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None
    privacy_policy_accepted: bool = True
    terms_of_service_accepted: bool = True

class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserInviteRequest(BaseModel):
    email: EmailStr
    role: str
    organization_id: Optional[int] = None

class UserManagementRequest(BaseModel):
    user_id: int
    action: str  # approve, reject, suspend, activate
    reason: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Authentication endpoints
@auth_router.post("/register")
async def register(request: Request, data: RegisterRequest):
    """Register a new user with email and password"""
    try:
        # Apply rate limiting
        rate_limit_error = SecurityMiddleware.check_rate_limit(request, 'auth', 'register')
        if rate_limit_error:
            raise rate_limit_error
        
        # Validate compliance
        if not data.privacy_policy_accepted or not data.terms_of_service_accepted:
            raise HTTPException(
                status_code=400, 
                detail="Privacy policy and terms of service must be accepted"
            )
        
        # Check if user already exists
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        c.execute('SELECT id, is_email_verified, auth_provider FROM users WHERE email = ?', (data.email,))
        existing_user = c.fetchone()
        conn.close()
        
        if existing_user:
            user_id, is_verified, auth_provider = existing_user
            if not is_verified:
                # User exists but email not verified - resend verification
                from email_service import email_service
                verification_token = AuthService.generate_verification_token()
                
                # Update verification token
                conn = sqlite3.connect(AUTH_DB)
                c = conn.cursor()
                c.execute('UPDATE users SET email_verification_token = ? WHERE id = ?', 
                         (verification_token, user_id))
                conn.commit()
                conn.close()
                
                # Send verification email
                display_name = data.full_name.strip() or data.email.split('@')[0]
                email_service.send_verification_email(data.email, verification_token, display_name)
                
                return {
                    "message": "User already exists but email not verified. Verification email sent.",
                    "user_id": user_id,
                    "email_sent": True,
                    "action": "verification_resent"
                }
            else:
                # User exists and verified - redirect to login
                return {
                    "message": "User already exists. Please login instead.",
                    "action": "redirect_to_login",
                    "auth_provider": auth_provider
                }
        
        # Parse full name into first and last name
        name_parts = data.full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user with email verification
        user_id = AuthService.create_user(
            email=data.email,
            password=data.password,
            first_name=first_name,
            last_name=last_name,
            username=data.username,
            organization_name=data.organization_name,
            role=UserRole.GENERAL_USER,
            auth_provider=AuthProvider.EMAIL,
            send_verification=True
        )
        
        # Record compliance
        ip_address = request.client.host if request.client else None
        AuthService.record_compliance(
            user_id=user_id,
            privacy_accepted=data.privacy_policy_accepted,
            terms_accepted=data.terms_of_service_accepted,
            ip_address=ip_address
        )
        
        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": user_id,
            "email_sent": True,
            "action": "registration_complete"
        }
        
    except ValueError as e:
        # Handle specific auth errors
        error_msg = str(e)
        if "already exists" in error_msg:
            raise HTTPException(status_code=409, detail="User already exists. Please login instead.")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@auth_router.post("/login")
async def login(request: Request, response: Response, data: LoginRequest):
    """Login with email and password"""
    try:
        # Apply rate limiting
        rate_limit_error = SecurityMiddleware.check_rate_limit(request, 'auth', 'login')
        if rate_limit_error:
            raise rate_limit_error
        
        # Authenticate user
        user = AuthService.authenticate_user(data.email, data.password)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create session
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        session_token = AuthService.create_session(
            user_id=user['id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Set session cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return {
            "message": "Login successful",
            "user": user,
            "session_token": session_token
        }
        
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@auth_router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout the current user"""
    try:
        # Get session token
        session_token = None
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            session_token = authorization.split(" ")[1]
        elif "session_token" in request.cookies:
            session_token = request.cookies["session_token"]
        
        if session_token:
            AuthService.invalidate_session(session_token)
        
        # Clear session cookie
        response.delete_cookie("session_token")
        
        return {"message": "Logout successful"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@auth_router.post("/logout-all")
async def logout_all_devices(
    request: Request,
    response: Response, 
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Logout from all devices (invalidate all sessions)"""
    try:
        deleted_count = AuthService.invalidate_all_user_sessions(current_user['id'])
        
        # Clear session cookie
        response.delete_cookie("session_token")
        
        return {
            "message": f"Logged out from all devices successfully. {deleted_count} sessions invalidated.",
            "sessions_invalidated": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Logout all devices error: {e}")
        raise HTTPException(status_code=500, detail="Failed to logout from all devices")

@auth_router.get("/sessions")
async def get_active_sessions(request: Request, current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """Get all active sessions for the current user"""
    try:
        sessions = AuthService.get_user_active_sessions(current_user['id'])
        
        return {
            "active_sessions": sessions,
            "total_count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Get active sessions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve active sessions")

# Google OAuth endpoints
@auth_router.get("/google")
async def google_oauth_url():
    """Get Google OAuth authorization URL"""
    if not google_oauth.is_configured():
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    try:
        state = secrets.token_urlsafe(32)
        auth_url = google_oauth.get_authorization_url(state=state)
        
        return {
            "auth_url": auth_url,
            "state": state
        }
        
    except Exception as e:
        logger.error(f"Google OAuth URL error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate OAuth URL")

@auth_router.post("/google/callback")
async def google_oauth_callback(request: Request, response: Response, data: GoogleCallbackRequest):
    """Handle Google OAuth callback with authorization code"""
    if not google_oauth.is_configured():
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    try:
        # Exchange authorization code for tokens
        token_data = google_oauth.exchange_code_for_tokens(data.code)
        
        # Get user info from Google
        google_user = None
        if 'id_token' in token_data:
            google_user = google_oauth.verify_id_token(token_data['id_token'])
        
        if not google_user and 'access_token' in token_data:
            google_user = google_oauth.get_user_info(token_data['access_token'])
        
        if not google_user:
            raise HTTPException(status_code=401, detail="Failed to get user information from Google")
        
        # Check if user exists
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, email, first_name, last_name, role, organization_id, status
            FROM users 
            WHERE google_id = ? OR (email = ? AND auth_provider IN ('google', 'email'))
        ''', (google_user['google_id'], google_user['email']))
        
        existing_user = c.fetchone()
        
        if existing_user:
            # User exists, log them in
            user_id, email, first_name, last_name, role, org_id, status = existing_user
            
            if status != UserStatus.APPROVED.value:
                raise HTTPException(status_code=403, detail=f"Account status: {status}")
            
            # Update Google ID if not set
            c.execute('UPDATE users SET google_id = ?, last_login = ?, auth_provider = ? WHERE id = ?',
                     (google_user['google_id'], datetime.datetime.utcnow().isoformat(), 'google', user_id))
            conn.commit()
            
            user = {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role,
                "organization_id": org_id
            }
        else:
            # Create new user
            if not data.privacy_policy_accepted or not data.terms_of_service_accepted:
                raise HTTPException(
                    status_code=400,
                    detail="Privacy policy and terms of service must be accepted"
                )
            
            user_id = AuthService.create_user(
                email=google_user['email'],
                first_name=google_user['first_name'],
                last_name=google_user['last_name'],
                role=UserRole.GENERAL_USER,
                auth_provider=AuthProvider.GOOGLE,
                google_id=google_user['google_id']
            )
            
            # Record compliance
            ip_address = request.client.host if request.client else None
            AuthService.record_compliance(
                user_id=user_id,
                privacy_accepted=data.privacy_policy_accepted,
                terms_accepted=data.terms_of_service_accepted,
                ip_address=ip_address
            )
            
            user = {
                "id": user_id,
                "email": google_user['email'],
                "first_name": google_user['first_name'],
                "last_name": google_user['last_name'],
                "role": UserRole.GENERAL_USER.value,
                "organization_id": None
            }
        
        conn.close()
        
        # Create session
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        session_token = AuthService.create_session(
            user_id=user['id'],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Set session cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=False,  # Set to True in production
            samesite="lax"
        )
        
        return {
            "message": "Google login successful",
            "user": user,
            "session_token": session_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        raise HTTPException(status_code=500, detail="Google authentication failed")

# Profile management endpoints
@auth_router.get("/profile")
async def get_profile(request: Request, current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """Get current user's profile with complete information"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        # Fetch complete user data with organization name
        c.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, u.role, u.organization_id, 
                   u.status, u.is_email_verified, u.created_at, u.last_login, u.auth_provider,
                   u.preferred_language, u.timezone, o.name as organization_name
            FROM users u
            LEFT JOIN organizations o ON u.organization_id = o.id
            WHERE u.id = ?
        ''', (current_user['id'],))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            (user_id, email, first_name, last_name, username, role, org_id, status, is_verified, 
             created_at, last_login, auth_provider, preferred_language, timezone, org_name) = result
            
            return {
                "user": {
                    "id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "full_name": f"{first_name} {last_name}".strip() if first_name or last_name else "",
                    "role": role,
                    "organization_id": org_id,
                    "organization_name": org_name,
                    "status": status,
                    "is_email_verified": bool(is_verified),
                    "is_approved": status == "approved",
                    "is_active": status == "approved",
                    "created_at": created_at,
                    "last_login": last_login,
                    "auth_provider": auth_provider,
                    "preferred_language": preferred_language,
                    "timezone": timezone
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@auth_router.put("/profile")
async def update_profile(
    request: Request,
    data: ProfileUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Update current user's profile"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        # Build update query dynamically
        updates = []
        values = []
        
        if data.first_name is not None:
            updates.append("first_name = ?")
            values.append(data.first_name)
        
        if data.last_name is not None:
            updates.append("last_name = ?")
            values.append(data.last_name)
        
        if data.username is not None:
            updates.append("username = ?")
            values.append(data.username)
        
        if data.preferred_language is not None:
            updates.append("preferred_language = ?")
            values.append(data.preferred_language)
        
        if data.timezone is not None:
            updates.append("timezone = ?")
            values.append(data.timezone)
        
        if updates:
            updates.append("updated_at = ?")
            values.append(datetime.datetime.utcnow().isoformat())
            values.append(current_user['id'])
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            c.execute(query, values)
            conn.commit()
        
        # Fetch and return the updated user data with all fields
        c.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, u.role, u.organization_id, 
                   u.status, u.is_email_verified, u.created_at, u.last_login, u.auth_provider,
                   u.preferred_language, u.timezone, o.name as organization_name
            FROM users u
            LEFT JOIN organizations o ON u.organization_id = o.id
            WHERE u.id = ?
        ''', (current_user['id'],))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            (user_id, email, first_name, last_name, username, role, org_id, status, is_verified, 
             created_at, last_login, auth_provider, preferred_language, timezone, org_name) = result
            
            return {
                "id": user_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "full_name": f"{first_name} {last_name}".strip() if first_name or last_name else "",
                "role": role,
                "organization_id": org_id,
                "organization_name": org_name,
                "status": status,
                "is_email_verified": bool(is_verified),
                "is_approved": status == "approved",
                "is_active": status == "approved",
                "created_at": created_at,
                "last_login": last_login,
                "auth_provider": auth_provider,
                "preferred_language": preferred_language,
                "timezone": timezone
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")

@auth_router.post("/password/change")
@require_auth
@log_activity("password_changed", "profile")
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Change user's password"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        # Verify current password
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('SELECT password_hash FROM users WHERE id = ?', (current_user['id'],))
        result = c.fetchone()
        
        if not result or not AuthService.verify_password(data.current_password, result[0]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        new_password_hash = AuthService.hash_password(data.new_password)
        c.execute(
            'UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?',
            (new_password_hash, datetime.datetime.utcnow().isoformat(), current_user['id'])
        )
        conn.commit()
        conn.close()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")

# User management endpoints (for organization users and admins)
@auth_router.get("/users")
@require_permission("user_view_general")
@log_activity("users_viewed", "users")
async def get_users(
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Get list of users (filtered by permissions)"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        # Build query based on user permissions
        base_query = '''
            SELECT id, email, first_name, last_name, role, status, organization_id, 
                   auth_provider, created_at, last_login
            FROM users
            WHERE 1=1
        '''
        params = []
        
        # Filter based on user role
        if not PermissionChecker.is_super_admin(current_user):
            if PermissionChecker.is_organization_user(current_user):
                # Organization users can only see general users and users in their org
                base_query += " AND (role = 'general_user' OR organization_id = ?)"
                params.append(current_user.get('organization_id'))
            else:
                # General users shouldn't access this endpoint, but just in case
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Additional filters
        if status:
            base_query += " AND status = ?"
            params.append(status)
        
        if role:
            base_query += " AND role = ?"
            params.append(role)
        
        base_query += " ORDER BY created_at DESC"
        
        c.execute(base_query, params)
        users = c.fetchall()
        conn.close()
        
        # Format response
        user_list = []
        for user in users:
            user_list.append({
                "id": user[0],
                "email": user[1],
                "first_name": user[2],
                "last_name": user[3],
                "role": user[4],
                "status": user[5],
                "organization_id": user[6],
                "auth_provider": user[7],
                "created_at": user[8],
                "last_login": user[9]
            })
        
        return {"users": user_list}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@auth_router.post("/users/invite")
@require_permission("user_create_general")
@log_activity("user_invited", "users")
async def invite_user(
    data: UserInviteRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Invite a new user"""
    try:
        # Validate role permissions
        if data.role == "super_admin" and not PermissionChecker.is_super_admin(current_user):
            raise HTTPException(status_code=403, detail="Cannot create super admin users")
        
        if data.role == "organization_user" and not PermissionChecker.is_super_admin(current_user):
            raise HTTPException(status_code=403, detail="Cannot create organization users")
        
        # Generate invitation
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        invitation_token = AuthService.generate_invitation_token()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        
        c.execute('''
            INSERT INTO user_invitations (
                email, role, organization_id, invited_by_user_id, 
                invitation_token, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.email, data.role, data.organization_id, current_user['id'],
            invitation_token, expires_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # In a real application, you would send an email here
        invitation_url = f"http://localhost:3000/auth/accept-invitation?token={invitation_token}"
        
        return {
            "message": "User invitation sent",
            "invitation_url": invitation_url,  # Remove this in production
            "expires_at": expires_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"User invitation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send invitation")

@auth_router.post("/users/manage")
@require_permission("user_view_all")
@log_activity("user_managed", "users")
async def manage_user(
    data: UserManagementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """Manage user status (approve, reject, suspend, activate)"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        valid_actions = ["approve", "reject", "suspend", "activate"]
        if data.action not in valid_actions:
            raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of: {valid_actions}")
        
        # Map actions to status
        action_status_map = {
            "approve": UserStatus.APPROVED.value,
            "reject": UserStatus.REJECTED.value,
            "suspend": UserStatus.SUSPENDED.value,
            "activate": UserStatus.APPROVED.value
        }
        
        new_status = action_status_map[data.action]
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        # Update user status
        c.execute(
            'UPDATE users SET status = ?, updated_at = ? WHERE id = ?',
            (new_status, datetime.datetime.utcnow().isoformat(), data.user_id)
        )
        
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        
        # Log the management action
        AuthService.log_activity(
            user_id=current_user['id'],
            action=f"user_{data.action}",
            resource="users",
            resource_id=str(data.user_id),
            details={"reason": data.reason} if data.reason else None
        )
        
        return {
            "message": f"User {data.action}d successfully",
            "user_id": data.user_id,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User management error: {e}")
        raise HTTPException(status_code=500, detail="User management failed")

# Utility endpoints
@auth_router.get("/me")
async def get_current_user_info(request: Request, current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """Get current user information"""
    return current_user

@auth_router.get("/permissions")
async def get_user_permissions(request: Request, current_user: Dict[str, Any] = Depends(get_current_user_required)):
    """Get current user's permissions"""
    try:
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('''
            SELECT p.name, p.description, p.resource, p.action
            FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role = ?
        ''', (current_user['role'],))
        
        permissions = c.fetchall()
        conn.close()
        
        permission_list = []
        for perm in permissions:
            permission_list.append({
                "name": perm[0],
                "description": perm[1],
                "resource": perm[2],
                "action": perm[3]
            })
        
        return {
            "role": current_user['role'],
            "permissions": permission_list
        }
        
    except Exception as e:
        logger.error(f"Get permissions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve permissions")

@auth_router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest):
    """Verify email address using verification token"""
    try:
        success = AuthService.verify_email(data.token)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Invalid or expired verification token"
            )
        
        return {
            "message": "Email verified successfully. You can now sign in.",
            "verified": True
        }
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")

@auth_router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest):
    """Resend email verification"""
    try:
        success = AuthService.resend_verification_email(data.email)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Unable to resend verification email. Please check if the email is correct."
            )
        
        return {
            "message": "Verification email sent. Please check your inbox.",
            "email_sent": True
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resend verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification email")

@auth_router.post("/forgot-password")
async def forgot_password(request: Request, data: ForgotPasswordRequest):
    """Initiate password reset flow"""
    try:
        # Apply rate limiting
        rate_limit_error = SecurityMiddleware.check_rate_limit(request, 'auth', 'forgot_password')
        if rate_limit_error:
            raise rate_limit_error
        
        success = AuthService.initiate_password_reset(data.email)
        
        # Always return success for security (don't reveal if email exists)
        return {
            "message": "If an account with that email exists, a password reset link has been sent.",
            "email_sent": True
        }
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Don't reveal error details for security
        return {
            "message": "If an account with that email exists, a password reset link has been sent.",
            "email_sent": True
        }

@auth_router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    """Reset password using reset token"""
    try:
        # Validate password strength
        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters long"
            )
        
        # Validate token first
        if not AuthService.validate_password_reset_token(data.token):
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired password reset token"
            )
        
        # Reset the password
        success = AuthService.reset_password_with_token(data.token, data.new_password)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired password reset token"
            )
        
        return {
            "message": "Password reset successfully. You can now login with your new password.",
            "reset_successful": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@auth_router.get("/validate-reset-token")
async def validate_reset_token(token: str):
    """Validate a password reset token"""
    try:
        is_valid = AuthService.validate_password_reset_token(token)
        
        return {
            "valid": is_valid,
            "message": "Token is valid" if is_valid else "Token is invalid or expired"
        }
        
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return {
            "valid": False,
            "message": "Token validation failed"
        } 