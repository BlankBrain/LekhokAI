"""
Google OAuth Service for KarigorAI

This module handles Google OAuth 2.0 authentication including
token validation and user profile retrieval.
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.auth import exceptions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Service for handling Google OAuth authentication"""
    
    def __init__(self):
        # Get Google OAuth credentials from environment
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        # Support multiple possible frontend ports (prioritize 3000)
        possible_ports = ['3000', '3001', '3002']
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        # If no explicit redirect URI, try to detect the frontend port
        if not self.redirect_uri:
            # First try port 3000 (default)
            self.redirect_uri = 'http://localhost:3000/auth/google/callback'
            
            # Verify if port 3000 is actually running
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', 3000))
                sock.close()
                
                # If port 3000 is not available, try others
                if result != 0:
                    for port in possible_ports[1:]:  # Skip 3000 since we already tried it
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(1)
                        result = sock.connect_ex(('localhost', int(port)))
                        sock.close()
                        if result == 0:
                            self.redirect_uri = f'http://localhost:{port}/auth/google/callback'
                            break
            except Exception:
                # Fallback to default
                self.redirect_uri = 'http://localhost:3000/auth/google/callback'
        
        # OAuth 2.0 scopes
        self.scopes = [
            'openid',
            'email', 
            'profile'
        ]
        
        if not self.client_id or not self.client_secret:
            logger.warning("Google OAuth credentials not configured. Google Sign-In will be disabled.")
    
    def is_configured(self) -> bool:
        """Check if Google OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        if not self.is_configured():
            raise ValueError("Google OAuth not configured")
        
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and ID tokens"""
        if not self.is_configured():
            raise ValueError("Google OAuth not configured")
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        
        if response.status_code != 200:
            logger.error(f"Failed to exchange code for tokens: {response.text}")
            raise ValueError("Failed to obtain tokens from Google")
        
        return response.json()
    
    def verify_id_token(self, id_token_str: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        if not self.is_configured():
            raise ValueError("Google OAuth not configured")
        
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'email_verified': idinfo.get('email_verified', False),
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'locale': idinfo.get('locale', 'en')
            }
            
        except exceptions.GoogleAuthError as e:
            logger.error(f"Failed to verify Google ID token: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid Google ID token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information using access token"""
        if not access_token:
            return None
        
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(user_info_url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Failed to get user info: {response.text}")
            return None
        
        user_data = response.json()
        
        return {
            'google_id': user_data.get('id'),
            'email': user_data.get('email'),
            'email_verified': user_data.get('verified_email', False),
            'first_name': user_data.get('given_name', ''),
            'last_name': user_data.get('family_name', ''),
            'name': user_data.get('name', ''),
            'picture': user_data.get('picture', ''),
            'locale': user_data.get('locale', 'en')
        }
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a Google access or refresh token"""
        if not token:
            return False
        
        revoke_url = f"https://oauth2.googleapis.com/revoke?token={token}"
        response = requests.post(revoke_url)
        
        return response.status_code == 200

class GoogleOAuthError(Exception):
    """Custom exception for Google OAuth errors"""
    pass

# Environment configuration helper
def setup_google_oauth_env():
    """Setup Google OAuth environment variables if not set"""
    env_file = '.env'
    
    required_vars = {
        'GOOGLE_CLIENT_ID': 'your_google_client_id_here',
        'GOOGLE_CLIENT_SECRET': 'your_google_client_secret_here',
        'GOOGLE_REDIRECT_URI': 'http://localhost:3000/auth/google/callback'
    }
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            existing_content = f.read()
    else:
        existing_content = ""
    
    new_vars = []
    for var, default_value in required_vars.items():
        if var not in existing_content and not os.getenv(var):
            new_vars.append(f"{var}={default_value}")
    
    if new_vars:
        with open(env_file, 'a') as f:
            if existing_content and not existing_content.endswith('\n'):
                f.write('\n')
            f.write('\n'.join(new_vars) + '\n')
        
        logger.info(f"Added Google OAuth environment variables to {env_file}")
        logger.info("Please update these with your actual Google OAuth credentials")

# Initialize environment setup
if __name__ == "__main__":
    setup_google_oauth_env() 