#!/usr/bin/env python3
"""
Manual Email Verification Utility for KarigorAI

This script allows admins to manually verify user emails when needed.
Usage: python3 verify_user_email.py <email>
"""

import sys
import sqlite3
import datetime
from auth_models import AUTH_DB, AuthService

def verify_user_email(email: str) -> bool:
    """Manually verify a user's email"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    
    try:
        # Find user
        c.execute('SELECT id, email, is_email_verified FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if not user:
            print(f"❌ User with email {email} not found")
            return False
        
        user_id, user_email, is_verified = user
        
        if is_verified:
            print(f"✅ Email {email} is already verified")
            return True
        
        # Update verification status
        c.execute('''
            UPDATE users 
            SET is_email_verified = 1, 
                email_verification_token = NULL,
                updated_at = ?
            WHERE id = ?
        ''', (datetime.datetime.utcnow().isoformat(), user_id))
        
        conn.commit()
        
        # Log the activity
        AuthService.log_activity(user_id, "email_verified_manually", "users", str(user_id))
        
        print(f"✅ Email {email} has been manually verified")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error verifying email: {e}")
        return False
    finally:
        conn.close()

def list_unverified_users():
    """List all unverified users"""
    conn = sqlite3.connect(AUTH_DB)
    c = conn.cursor()
    
    c.execute('''
        SELECT id, email, first_name, last_name, created_at 
        FROM users 
        WHERE is_email_verified = 0 AND auth_provider = 'email'
        ORDER BY created_at DESC
    ''')
    
    users = c.fetchall()
    conn.close()
    
    if not users:
        print("✅ No unverified users found")
        return
    
    print(f"\n📧 Found {len(users)} unverified users:")
    print("-" * 80)
    print(f"{'ID':<4} {'Email':<30} {'Name':<20} {'Created':<20}")
    print("-" * 80)
    
    for user in users:
        user_id, email, first_name, last_name, created_at = user
        name = f"{first_name} {last_name}".strip() or "N/A"
        created = created_at[:19] if created_at else "N/A"
        print(f"{user_id:<4} {email:<30} {name:<20} {created:<20}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 verify_user_email.py <email>     - Verify specific email")
        print("  python3 verify_user_email.py --list      - List unverified users")
        print("  python3 verify_user_email.py --help      - Show this help")
        return
    
    command = sys.argv[1]
    
    if command in ['--help', '-h']:
        print(__doc__)
        return
    elif command in ['--list', '-l']:
        list_unverified_users()
        return
    else:
        email = command
        verify_user_email(email)

if __name__ == "__main__":
    main() 