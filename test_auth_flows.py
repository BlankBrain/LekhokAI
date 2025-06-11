#!/usr/bin/env python3
"""
Comprehensive Authentication Flow Testing Script for Lekhok

This script tests all authentication flows:
1. Email/Password Registration
2. Email Verification
3. Login Flow
4. Password Reset Flow
5. Google OAuth Flow (manual)
6. Session Management
7. Security Features

Run this script to verify all authentication features are working correctly.
"""

import requests
import json
import time
import sys
import os
from typing import Dict, Optional

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"

# Test user data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpass123",
    "username": "testuser",
    "full_name": "Test User",
    "organization_name": "Test Organization"
}

class AuthFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_server_health(self) -> bool:
        """Test if backend server is running"""
        try:
            response = self.session.get(f"{API_BASE}/system/health")
            if response.status_code == 200:
                self.log_test("Backend Server Health", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Backend Server Health", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Server Health", False, f"Connection error: {e}")
            return False
    
    def test_email_registration(self) -> Optional[Dict]:
        """Test email/password registration"""
        try:
            # Clean up any existing user first
            self.cleanup_test_user()
            
            payload = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"],
                "username": TEST_USER["username"],
                "full_name": TEST_USER["full_name"],
                "organization_name": TEST_USER["organization_name"],
                "privacy_policy_accepted": True,
                "terms_of_service_accepted": True
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Email Registration", True, 
                            f"User created with ID: {data.get('user_id')}")
                return data
            else:
                self.log_test("Email Registration", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Email Registration", False, f"Exception: {e}")
            return None
    
    def test_email_verification(self) -> bool:
        """Test email verification (requires manual token from logs/email)"""
        print("\n📧 EMAIL VERIFICATION TEST")
        print("Check your email or server logs for verification token...")
        
        token = input("Enter verification token (or press Enter to skip): ").strip()
        
        if not token:
            self.log_test("Email Verification", False, "Skipped - no token provided")
            return False
        
        try:
            payload = {"token": token}
            response = self.session.post(f"{API_BASE}/auth/verify-email", json=payload)
            
            if response.status_code == 200:
                self.log_test("Email Verification", True, "Email verified successfully")
                return True
            else:
                self.log_test("Email Verification", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Email Verification", False, f"Exception: {e}")
            return False
    
    def test_login(self) -> bool:
        """Test login flow"""
        try:
            payload = {
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('session_token')
                
                if self.auth_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}',
                        'X-Session-Token': self.auth_token
                    })
                    
                    self.log_test("Login", True, "Login successful, token received")
                    return True
                else:
                    self.log_test("Login", False, "No auth token in response")
                    return False
            else:
                self.log_test("Login", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Login", False, f"Exception: {e}")
            return False
    
    def test_profile_access(self) -> bool:
        """Test accessing user profile (requires authentication)"""
        try:
            response = self.session.get(f"{API_BASE}/auth/profile")
            
            if response.status_code == 200:
                data = response.json()
                user = data.get('user', {})
                self.log_test("Profile Access", True, 
                            f"Retrieved profile for: {user.get('email')}")
                return True
            else:
                self.log_test("Profile Access", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Profile Access", False, f"Exception: {e}")
            return False
    
    def test_password_reset_request(self) -> bool:
        """Test forgot password flow"""
        try:
            payload = {"email": TEST_USER["email"]}
            response = self.session.post(f"{API_BASE}/auth/forgot-password", json=payload)
            
            if response.status_code == 200:
                self.log_test("Password Reset Request", True, 
                            "Reset email sent (check logs for token)")
                return True
            else:
                self.log_test("Password Reset Request", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Password Reset Request", False, f"Exception: {e}")
            return False
    
    def test_password_reset_completion(self) -> bool:
        """Test password reset completion (requires manual token)"""
        print("\n🔑 PASSWORD RESET TEST")
        print("Check your email or server logs for password reset token...")
        
        token = input("Enter password reset token (or press Enter to skip): ").strip()
        
        if not token:
            self.log_test("Password Reset Completion", False, "Skipped - no token provided")
            return False
        
        try:
            new_password = "newpassword123"
            payload = {
                "token": token,
                "new_password": new_password
            }
            
            response = self.session.post(f"{API_BASE}/auth/reset-password", json=payload)
            
            if response.status_code == 200:
                # Update test user password for future tests
                TEST_USER["password"] = new_password
                self.log_test("Password Reset Completion", True, "Password reset successful")
                return True
            else:
                self.log_test("Password Reset Completion", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Password Reset Completion", False, f"Exception: {e}")
            return False
    
    def test_session_management(self) -> bool:
        """Test session management features"""
        try:
            # Test get active sessions
            response = self.session.get(f"{API_BASE}/auth/sessions")
            
            if response.status_code == 200:
                data = response.json()
                session_count = data.get('total_count', 0)
                self.log_test("Get Active Sessions", True, 
                            f"Found {session_count} active sessions")
                
                # Test logout from all devices
                response = self.session.post(f"{API_BASE}/auth/logout-all")
                
                if response.status_code == 200:
                    data = response.json()
                    invalidated = data.get('sessions_invalidated', 0)
                    self.log_test("Logout All Devices", True, 
                                f"Invalidated {invalidated} sessions")
                    return True
                else:
                    self.log_test("Logout All Devices", False, 
                                f"Status: {response.status_code}")
                    return False
            else:
                self.log_test("Get Active Sessions", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Session Management", False, f"Exception: {e}")
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting on login endpoint"""
        try:
            # Attempt multiple rapid login requests
            failed_attempts = 0
            
            for i in range(7):  # Try more than the rate limit (5)
                payload = {
                    "email": "nonexistent@example.com",
                    "password": "wrongpassword"
                }
                
                response = self.session.post(f"{API_BASE}/auth/login", json=payload)
                
                if response.status_code == 429:  # Rate limited
                    self.log_test("Rate Limiting", True, 
                                f"Rate limit triggered after {i+1} attempts")
                    return True
                elif response.status_code == 401:  # Expected for wrong credentials
                    failed_attempts += 1
                    time.sleep(0.1)  # Small delay between requests
            
            # If we get here, rate limiting might not be working
            self.log_test("Rate Limiting", False, 
                        f"No rate limit after {failed_attempts} failed attempts")
            return False
            
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Exception: {e}")
            return False
    
    def test_google_oauth_setup(self) -> bool:
        """Test Google OAuth configuration"""
        try:
            response = self.session.get(f"{API_BASE}/auth/google")
            
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url')
                if auth_url and 'accounts.google.com' in auth_url:
                    self.log_test("Google OAuth Setup", True, 
                                "Google OAuth URL generated successfully")
                    print(f"   Google OAuth URL: {auth_url[:50]}...")
                    return True
                else:
                    self.log_test("Google OAuth Setup", False, 
                                "Invalid Google OAuth URL")
                    return False
            elif response.status_code == 501:
                self.log_test("Google OAuth Setup", False, 
                            "Google OAuth not configured (missing credentials)")
                return False
            else:
                self.log_test("Google OAuth Setup", False, 
                            f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Google OAuth Setup", False, f"Exception: {e}")
            return False
    
    def cleanup_test_user(self):
        """Clean up test user from database (for testing)"""
        try:
            # This would require admin privileges in a real system
            # For testing, we'll just attempt and ignore failures
            pass
        except:
            pass
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧪 AUTHENTICATION FLOW TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\nFailed Tests:")
        for result in self.test_results:
            if not result['success']:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\nTest Coverage:")
        print("  ✅ Email Registration")
        print("  📧 Email Verification (manual)")
        print("  🔐 Login Flow")
        print("  👤 Profile Access")
        print("  🔑 Password Reset Request")
        print("  🔑 Password Reset Completion (manual)")
        print("  📱 Session Management")
        print("  🛡️ Rate Limiting")
        print("  🌐 Google OAuth Setup")
        
        return passed == total

def main():
    """Run all authentication flow tests"""
    print("🚀 Starting Authentication Flow Tests")
    print("="*60)
    
    tester = AuthFlowTester()
    
    # Check if servers are running
    if not tester.test_server_health():
        print("\n❌ Backend server is not running!")
        print("Please start the server with: uvicorn api_server:app --reload")
        return False
    
    print("\n📝 Running Authentication Tests...")
    
    # Core authentication flow
    registration_data = tester.test_email_registration()
    if registration_data:
        tester.test_email_verification()  # Manual step
        
        if tester.test_login():
            tester.test_profile_access()
            tester.test_session_management()
    
    # Password reset flow
    tester.test_password_reset_request()
    tester.test_password_reset_completion()  # Manual step
    
    # Security and OAuth tests
    tester.test_rate_limiting()
    tester.test_google_oauth_setup()
    
    # Print summary
    all_passed = tester.print_summary()
    
    if all_passed:
        print("\n🎉 All authentication flows are working correctly!")
    else:
        print("\n⚠️ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 