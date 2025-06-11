#!/usr/bin/env python3
"""
Authentication System Initialization Script for KarigorAI

This script initializes the authentication system by:
1. Creating database tables
2. Setting up default permissions and roles
3. Creating the first super admin user
4. Setting up Google OAuth environment variables
"""

import os
import sys
import getpass
from auth_models import init_auth_db, AuthService, UserRole
from google_oauth import setup_google_oauth_env

def create_super_admin():
    """Create the first super admin user"""
    print("\n🔐 Creating Super Admin User")
    print("=" * 40)
    
    while True:
        email = input("Enter super admin email: ").strip()
        if email and "@" in email:
            break
        print("Please enter a valid email address.")
    
    while True:
        password = getpass.getpass("Enter password (min 6 characters): ")
        if len(password) >= 6:
            confirm_password = getpass.getpass("Confirm password: ")
            if password == confirm_password:
                break
            else:
                print("Passwords don't match. Please try again.")
        else:
            print("Password must be at least 6 characters long.")
    
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    
    try:
        # Check if user already exists
        import sqlite3
        from auth_models import AUTH_DB
        
        conn = sqlite3.connect(AUTH_DB)
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        existing_user = c.fetchone()
        conn.close()
        
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return False
        
        # Create super admin user
        user_id = AuthService.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.SUPER_ADMIN,
            auto_approve=True
        )
        
        print(f"✅ Super admin user created successfully!")
        print(f"   User ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Name: {first_name} {last_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("\n🌐 Setting up Environment Variables")
    print("=" * 40)
    
    # Setup Google OAuth environment variables
    setup_google_oauth_env()
    
    # Check for API keys
    if not os.getenv('GOOGLE_API_KEY'):
        print("\n📝 Don't forget to set up your environment variables:")
        print("   - GOOGLE_API_KEY (for story and image generation)")
        print("   - GOOGLE_CLIENT_ID (for Google OAuth)")
        print("   - GOOGLE_CLIENT_SECRET (for Google OAuth)")
        print("   - GOOGLE_REDIRECT_URI (for Google OAuth)")

def display_summary():
    """Display initialization summary"""
    print("\n🎉 Authentication System Initialized!")
    print("=" * 50)
    print("✅ Database tables created")
    print("✅ Permissions and roles configured")
    print("✅ Super admin user created")
    print("✅ Environment configuration ready")
    print("\n🚀 Next Steps:")
    print("1. Update .env file with your actual credentials")
    print("2. Start the API server: python api_server.py")
    print("3. Start the UI: cd ui && npm run dev")
    print("4. Visit http://localhost:3000/auth to test authentication")
    print("\n📚 User Roles Available:")
    print("   - Super Admin: Full system access")
    print("   - Organization User: Manage users and characters")
    print("   - General User: Story generation and personal management")

def main():
    """Main initialization function"""
    print("🚀 KarigorAI Authentication System Initialization")
    print("=" * 60)
    
    # Initialize database
    print("\n📊 Initializing Database...")
    try:
        init_auth_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Create super admin
    if not create_super_admin():
        print("\n❌ Super admin creation failed. Exiting...")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Display summary
    display_summary()

if __name__ == "__main__":
    main() 