"""
Authentication Models and Database Schema for KarigorAI

This module defines the database models for the role-based authentication system
including users, roles, organizations, sessions, and audit logging.
"""

import sqlite3
import datetime
import hashlib
import secrets
import bcrypt
import logging
from typing import Optional, Dict, List, Any
from enum import Enum
import json

# Configure logging
logger = logging.getLogger(__name__)

# Database file
AUTH_DB = 'auth.db'

class UserRole(Enum):
    GENERAL_USER = "general_user"
    ORGANIZATION_USER = "organization_user"
    SUPER_ADMIN = "super_admin"

class UserStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

class AuthProvider(Enum):
    EMAIL = "email"
    GOOGLE = "google"
    FACEBOOK = "facebook"  # Future
    APPLE = "apple"        # Future

def init_auth_db():
    """Initialize the authentication database with all required tables"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            first_name TEXT,
            last_name TEXT,
            role TEXT NOT NULL DEFAULT 'general_user',
            status TEXT NOT NULL DEFAULT 'pending',
            organization_id INTEGER,
            auth_provider TEXT NOT NULL DEFAULT 'email',
            google_id TEXT UNIQUE,
            profile_picture_url TEXT,
            preferred_language TEXT DEFAULT 'en',
            timezone TEXT DEFAULT 'UTC',
            is_email_verified BOOLEAN DEFAULT FALSE,
            email_verification_token TEXT,
            password_reset_token TEXT,
            password_reset_expires DATETIME,
            last_login DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id)
        )
    ''')
    
    # Organizations table
    c.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            domain TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            admin_user_id INTEGER,
            max_users INTEGER DEFAULT 100,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_user_id) REFERENCES users (id)
        )
    ''')
    
    # Sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            ip_address TEXT,
            user_agent TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Permissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Role permissions mapping
    c.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            permission_id INTEGER NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (permission_id) REFERENCES permissions (id)
        )
    ''')
    
    # User activity audit log
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Compliance tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_compliance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            privacy_policy_accepted BOOLEAN DEFAULT FALSE,
            terms_of_service_accepted BOOLEAN DEFAULT FALSE,
            privacy_policy_version TEXT,
            terms_version TEXT,
            accepted_at DATETIME,
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # User invitations
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            organization_id INTEGER,
            invited_by_user_id INTEGER NOT NULL,
            invitation_token TEXT UNIQUE NOT NULL,
            expires_at DATETIME NOT NULL,
            is_accepted BOOLEAN DEFAULT FALSE,
            accepted_at DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES organizations (id),
            FOREIGN KEY (invited_by_user_id) REFERENCES users (id)
        )
    ''')
    
    # Initialize default permissions
    _init_default_permissions(c)
    
    conn.commit()
    conn.close()

def _init_default_permissions(cursor):
    """Initialize default permissions for the system"""
    permissions = [
        # Story generation permissions
        ("story_generate", "Generate stories", "stories", "create"),
        ("story_view_own", "View own stories", "stories", "read_own"),
        ("story_edit_own", "Edit own stories", "stories", "update_own"),
        ("story_delete_own", "Delete own stories", "stories", "delete_own"),
        
        # Character permissions
        ("character_view", "View characters", "characters", "read"),
        ("character_create", "Create characters", "characters", "create"),
        ("character_edit", "Edit characters", "characters", "update"),
        ("character_delete", "Delete characters", "characters", "delete"),
        
        # User management permissions
        ("user_view_general", "View general users", "users", "read_general"),
        ("user_create_general", "Create general users", "users", "create_general"),
        ("user_edit_general", "Edit general users", "users", "update_general"),
        ("user_delete_general", "Delete general users", "users", "delete_general"),
        ("user_view_org", "View organization users", "users", "read_org"),
        ("user_create_org", "Create organization users", "users", "create_org"),
        ("user_edit_org", "Edit organization users", "users", "update_org"),
        ("user_delete_org", "Delete organization users", "users", "delete_org"),
        ("user_view_all", "View all users", "users", "read_all"),
        
        # Organization permissions
        ("org_manage", "Manage organization", "organizations", "manage"),
        ("org_view_stats", "View organization statistics", "organizations", "stats"),
        
        # System permissions
        ("system_admin", "System administration", "system", "admin"),
        ("system_analytics", "View system analytics", "system", "analytics"),
        ("system_settings", "Manage system settings", "system", "settings"),
        
        # Profile permissions
        ("profile_view_own", "View own profile", "profile", "read_own"),
        ("profile_edit_own", "Edit own profile", "profile", "update_own"),
    ]
    
    for name, description, resource, action in permissions:
        cursor.execute('''
            INSERT OR IGNORE INTO permissions (name, description, resource, action)
            VALUES (?, ?, ?, ?)
        ''', (name, description, resource, action))
    
    # Map permissions to roles
    role_permission_mapping = {
        UserRole.GENERAL_USER.value: [
            "story_generate", "story_view_own", "story_edit_own", "story_delete_own",
            "character_view", "profile_view_own", "profile_edit_own"
        ],
        UserRole.ORGANIZATION_USER.value: [
            "story_generate", "story_view_own", "story_edit_own", "story_delete_own",
            "character_view", "character_create", "character_edit", "character_delete",
            "user_view_general", "user_create_general", "user_edit_general",
            "profile_view_own", "profile_edit_own", "org_view_stats"
        ],
        UserRole.SUPER_ADMIN.value: [
            "story_generate", "story_view_own", "story_edit_own", "story_delete_own",
            "character_view", "character_create", "character_edit", "character_delete",
            "user_view_all", "user_create_general", "user_edit_general", "user_delete_general",
            "user_create_org", "user_edit_org", "user_delete_org",
            "org_manage", "org_view_stats", "system_admin", "system_analytics",
            "system_settings", "profile_view_own", "profile_edit_own"
        ]
    }
    
    for role, permissions in role_permission_mapping.items():
        for permission_name in permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO role_permissions (role, permission_id)
                SELECT ?, id FROM permissions WHERE name = ?
            ''', (role, permission_name))

class AuthService:
    """Service class for authentication operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_invitation_token() -> str:
        """Generate a secure invitation token"""
        return secrets.token_urlsafe(24)
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure email verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_user(email: str, password: str = None, first_name: str = "", last_name: str = "", 
                   username: str = "", organization_name: str = "",
                   role: UserRole = UserRole.GENERAL_USER, auth_provider: AuthProvider = AuthProvider.EMAIL,
                   google_id: str = None, auto_approve: bool = False, send_verification: bool = True) -> int:
        """Create a new user"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            # Check if user already exists
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            if c.fetchone():
                raise ValueError(f"User with email {email} already exists")
            
            # Handle organization creation if provided
            organization_id = None
            if organization_name and organization_name.strip():
                # Check if organization exists
                c.execute('SELECT id FROM organizations WHERE name = ?', (organization_name.strip(),))
                org_result = c.fetchone()
                
                if org_result:
                    organization_id = org_result[0]
                else:
                    # Create new organization
                    c.execute('''
                        INSERT INTO organizations (name, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        organization_name.strip(),
                        'pending',
                        datetime.datetime.utcnow().isoformat(),
                        datetime.datetime.utcnow().isoformat()
                    ))
                    organization_id = c.lastrowid
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = AuthService.hash_password(password)
            
            # Set initial status
            initial_status = UserStatus.APPROVED if auto_approve else UserStatus.PENDING
            if role == UserRole.SUPER_ADMIN:
                initial_status = UserStatus.APPROVED  # Super admins are always approved
            
            # For email registration, auto-approve but require email verification
            if auth_provider == AuthProvider.EMAIL:
                initial_status = UserStatus.APPROVED
            
            # Generate email verification token for email users
            verification_token = None
            is_email_verified = auth_provider == AuthProvider.GOOGLE  # Google users are pre-verified
            if auth_provider == AuthProvider.EMAIL and send_verification:
                verification_token = AuthService.generate_verification_token()
            
            # Insert user
            c.execute('''
                INSERT INTO users (
                    email, password_hash, first_name, last_name, role, 
                    auth_provider, google_id, status, organization_id, 
                    is_email_verified, email_verification_token, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                email, password_hash, first_name, last_name, role.value,
                auth_provider.value, google_id, initial_status.value, organization_id,
                is_email_verified, verification_token,
                datetime.datetime.utcnow().isoformat(),
                datetime.datetime.utcnow().isoformat()
            ))
            
            user_id = c.lastrowid
            
            # Update organization admin if it was just created
            if organization_id and organization_name:
                c.execute('UPDATE organizations SET admin_user_id = ? WHERE id = ?', 
                         (user_id, organization_id))
            
            conn.commit()
            
            # Send verification email if needed
            if verification_token and send_verification:
                from email_service import email_service
                display_name = f"{first_name} {last_name}".strip() or email.split('@')[0]
                email_service.send_verification_email(email, verification_token, display_name)
            
            return user_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user with email and password"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, email, password_hash, first_name, last_name, role, status,
                   organization_id, is_email_verified
            FROM users 
            WHERE email = ? AND auth_provider = 'email'
        ''', (email,))
        
        user = c.fetchone()
        conn.close()
        
        if not user:
            return None
        
        user_id, email, password_hash, first_name, last_name, role, status, org_id, is_verified = user
        
        if not AuthService.verify_password(password, password_hash):
            return None
        
        if status != UserStatus.APPROVED.value:
            raise ValueError(f"Account status: {status}")
        
        if not is_verified:
            raise ValueError("Email not verified")
        
        # Update last login
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        c.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                 (datetime.datetime.utcnow().isoformat(), user_id))
        conn.commit()
        conn.close()
        
        return {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "organization_id": org_id,
            "status": status,
            "is_email_verified": bool(is_verified),
            "is_approved": status == UserStatus.APPROVED.value,
            "is_active": status == UserStatus.APPROVED.value
        }
    
    @staticmethod
    def create_session(user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new session for a user"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        session_token = AuthService.generate_session_token()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        
        c.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at, is_active, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_token, expires_at.isoformat(), True, ip_address, user_agent))
        
        conn.commit()
        conn.close()
        
        AuthService.log_activity(user_id, "session_created", "sessions", session_token[:8])
        
        return session_token
    
    @staticmethod
    def validate_session(session_token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return user info"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('''
            SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.organization_id, s.expires_at, u.status, u.is_email_verified
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ? AND s.is_active = TRUE AND u.status = 'approved'
        ''', (session_token,))
        
        result = c.fetchone()
        conn.close()
        
        if not result:
            return None
        
        user_id, email, first_name, last_name, role, org_id, expires_at, status, is_verified = result
        
        # Check if session is expired
        expires_datetime = datetime.datetime.fromisoformat(expires_at)
        if expires_datetime < datetime.datetime.utcnow():
            AuthService.invalidate_session(session_token)
            return None
        
        return {
            "id": user_id,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "organization_id": org_id,
            "status": status,
            "is_email_verified": bool(is_verified),
            "is_approved": status == UserStatus.APPROVED.value,
            "is_active": status == UserStatus.APPROVED.value
        }
    
    @staticmethod
    def invalidate_session(session_token: str):
        """Invalidate a specific session"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            # Get user_id before deleting
            c.execute('SELECT user_id FROM sessions WHERE session_token = ?', (session_token,))
            result = c.fetchone()
            
            if result:
                user_id = result[0]
                
                # Delete the session
                c.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
                conn.commit()
                
                # Log the session invalidation
                AuthService.log_activity(user_id, "session_invalidated", "sessions", session_token[:8])
                
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def invalidate_all_user_sessions(user_id: int):
        """Invalidate all sessions for a specific user (logout from all devices)"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            # Delete all sessions for the user
            c.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            deleted_count = c.rowcount
            conn.commit()
            
            # Log the mass session invalidation
            AuthService.log_activity(user_id, "all_sessions_invalidated", "sessions", f"count:{deleted_count}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Mass session invalidation error: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def cleanup_expired_sessions():
        """Clean up expired sessions from the database"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            # Delete expired sessions
            current_time = datetime.datetime.utcnow().isoformat()
            c.execute('DELETE FROM sessions WHERE expires_at < ?', (current_time,))
            deleted_count = c.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} expired sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def get_user_active_sessions(user_id: int) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            current_time = datetime.datetime.utcnow().isoformat()
            c.execute('''
                SELECT session_token, created_at, expires_at, ip_address, user_agent
                FROM sessions 
                WHERE user_id = ? AND expires_at > ?
                ORDER BY created_at DESC
            ''', (user_id, current_time))
            
            sessions = []
            for row in c.fetchall():
                sessions.append({
                    "session_token": row[0][:8] + "...",  # Only show partial token for security
                    "created_at": row[1],
                    "expires_at": row[2],
                    "ip_address": row[3],
                    "user_agent": row[4]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Get user sessions error: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def has_permission(user_role: str, permission_name: str) -> bool:
        """Check if a user role has a specific permission"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        c.execute('''
            SELECT COUNT(*) FROM role_permissions rp
            JOIN permissions p ON rp.permission_id = p.id
            WHERE rp.role = ? AND p.name = ?
        ''', (user_role, permission_name))
        
        count = c.fetchone()[0]
        conn.close()
        
        return count > 0
    
    @staticmethod
    def log_activity(user_id: int, action: str, resource: str = None, 
                    resource_id: str = None, details: Dict = None,
                    ip_address: str = None, user_agent: str = None):
        """Log user activity"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        details_json = json.dumps(details) if details else None
        
        c.execute('''
            INSERT INTO audit_logs (user_id, action, resource, resource_id, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, action, resource, resource_id, details_json, ip_address, user_agent))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def record_compliance(user_id: int, privacy_accepted: bool = False, 
                         terms_accepted: bool = False, ip_address: str = None):
        """Record user compliance with privacy policy and terms"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        timestamp = datetime.datetime.utcnow().isoformat()
        
        c.execute('''
            INSERT OR REPLACE INTO user_compliance 
            (user_id, privacy_policy_accepted, terms_of_service_accepted, 
             privacy_policy_version, terms_version, accepted_at, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, privacy_accepted, terms_accepted, "1.0", "1.0", timestamp, ip_address))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def verify_email(verification_token: str) -> bool:
        """Verify email address using verification token"""
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        
        try:
            # Find user with this verification token
            c.execute('''
                SELECT id, email, first_name, last_name
                FROM users 
                WHERE email_verification_token = ? AND is_email_verified = FALSE
            ''', (verification_token,))
            
            user = c.fetchone()
            if not user:
                return False
            
            user_id, email, first_name, last_name = user
            
            # Mark email as verified and clear token
            c.execute('''
                UPDATE users 
                SET is_email_verified = TRUE, 
                    email_verification_token = NULL,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.datetime.utcnow().isoformat(), user_id))
            
            conn.commit()
            
            # Log the verification
            AuthService.log_activity(user_id, "email_verified", "users", str(user_id))
            
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def resend_verification_email(email: str) -> bool:
        """Resend email verification"""
        try:
            conn = sqlite3.connect(AUTH_DB)
            c = conn.cursor()
            
            # Get user info
            c.execute('''
                SELECT id, first_name, last_name, is_email_verified, auth_provider
                FROM users WHERE email = ? AND auth_provider = 'email'
            ''', (email,))
            
            result = c.fetchone()
            if not result:
                # Don't reveal if email doesn't exist
                return True
            
            user_id, first_name, last_name, is_verified, auth_provider = result
            
            if is_verified:
                # Email already verified
                return True
            
            # Generate new verification token
            verification_token = AuthService.generate_verification_token()
            
            # Update user with new token
            c.execute('''
                UPDATE users SET email_verification_token = ?, updated_at = ?
                WHERE id = ?
            ''', (verification_token, datetime.datetime.utcnow().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            # Send verification email
            from email_service import email_service
            display_name = f"{first_name} {last_name}".strip() or email.split('@')[0]
            return email_service.send_verification_email(email, verification_token, display_name)
            
        except Exception as e:
            logger.error(f"Resend verification error: {e}")
            return False
    
    @staticmethod
    def initiate_password_reset(email: str) -> bool:
        """Initiate password reset process"""
        try:
            conn = sqlite3.connect(AUTH_DB)
            c = conn.cursor()
            
            # Check if user exists with email auth provider
            c.execute('''
                SELECT id, first_name, last_name, is_email_verified, auth_provider
                FROM users WHERE email = ? AND auth_provider = 'email'
            ''', (email,))
            
            result = c.fetchone()
            if not result:
                # Don't reveal if email doesn't exist for security
                logger.info(f"Password reset requested for non-existent email: {email}")
                return True
            
            user_id, first_name, last_name, is_verified, auth_provider = result
            
            if not is_verified:
                # Email not verified - don't allow password reset
                logger.info(f"Password reset attempted for unverified email: {email}")
                return True
            
            # Generate password reset token
            reset_token = AuthService.generate_password_reset_token()
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1 hour expiry
            
            # Update user with reset token
            c.execute('''
                UPDATE users 
                SET password_reset_token = ?, password_reset_expires = ?, updated_at = ?
                WHERE id = ?
            ''', (reset_token, expires_at.isoformat(), datetime.datetime.utcnow().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            # Send password reset email
            from email_service import email_service
            display_name = f"{first_name} {last_name}".strip() or email.split('@')[0]
            success = email_service.send_password_reset_email(email, reset_token, display_name)
            
            # Log the password reset request
            AuthService.log_activity(user_id, "password_reset_requested", "auth", email)
            
            return success
            
        except Exception as e:
            logger.error(f"Password reset initiation error: {e}")
            return False
    
    @staticmethod
    def reset_password_with_token(reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            conn = sqlite3.connect(AUTH_DB)
            c = conn.cursor()
            
            # Find user with valid reset token
            c.execute('''
                SELECT id, email, password_reset_expires
                FROM users 
                WHERE password_reset_token = ? AND auth_provider = 'email'
            ''', (reset_token,))
            
            result = c.fetchone()
            if not result:
                logger.warning(f"Invalid password reset token attempted: {reset_token[:8]}...")
                return False
            
            user_id, email, expires_str = result
            
            # Check if token has expired
            if expires_str:
                expires_at = datetime.datetime.fromisoformat(expires_str)
                if datetime.datetime.utcnow() > expires_at:
                    logger.info(f"Expired password reset token for user {email}")
                    return False
            else:
                logger.warning(f"No expiry date for reset token: {reset_token[:8]}...")
                return False
            
            # Hash new password
            password_hash = AuthService.hash_password(new_password)
            
            # Update password and clear reset token
            c.execute('''
                UPDATE users 
                SET password_hash = ?, password_reset_token = NULL, 
                    password_reset_expires = NULL, updated_at = ?
                WHERE id = ?
            ''', (password_hash, datetime.datetime.utcnow().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            # Log the password reset completion
            AuthService.log_activity(user_id, "password_reset_completed", "auth", email)
            
            return True
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return False
    
    @staticmethod
    def validate_password_reset_token(reset_token: str) -> bool:
        """Validate a password reset token without resetting"""
        try:
            conn = sqlite3.connect(AUTH_DB)
            c = conn.cursor()
            
            c.execute('''
                SELECT password_reset_expires
                FROM users 
                WHERE password_reset_token = ? AND auth_provider = 'email'
            ''', (reset_token,))
            
            result = c.fetchone()
            if not result:
                return False
            
            expires_str = result[0]
            if expires_str:
                expires_at = datetime.datetime.fromisoformat(expires_str)
                return datetime.datetime.utcnow() <= expires_at
            
            return False
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False

# Initialize the database when the module is imported
init_auth_db() 