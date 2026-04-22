"""
Quick fix script to restore login access for all existing users.
Run this script to fix the authentication issue.

Usage:
    python manage.py shell < fix_users_quick.py

Or use the management command:
    python manage.py fix_users
"""

from django.db import transaction
from django.utils import timezone
from apps.accounts.models import User

def fix_all_users():
    """Fix all existing users to restore login access."""
    
    print("\n" + "="*50)
    print("FIXING USER ACCOUNTS")
    print("="*50 + "\n")
    
    users = User.objects.all()
    fixed = []
    
    with transaction.atomic():
        for user in users:
            changes = []
            
            # Fix is_active - restore access if not explicitly banned
            if not user.is_active and not user.ban_reason:
                user.is_active = True
                changes.append("is_active → True")
            
            # Fix status - approve pending users for backward compatibility
            if user.status == User.Status.PENDING:
                user.status = User.Status.APPROVED
                changes.append("status → approved")
            
            # Fix role - ensure valid role
            if not user.role or user.role not in [r[0] for r in User.Role.choices]:
                user.role = User.Role.ATTENDEE
                changes.append("role → attendee")
            
            if changes:
                user.updated_at = timezone.now()
                user.save()
                fixed.append((user.email, changes))
                print(f"✓ Fixed: {user.email}")
                for change in changes:
                    print(f"    - {change}")
    
    print(f"\n{'='*50}")
    print(f"Total users: {users.count()}")
    print(f"Fixed: {len(fixed)}")
    print(f"Already OK: {users.count() - len(fixed)}")
    print("="*50 + "\n")
    
    if fixed:
        print("SUCCESS: All users can now log in!")
    else:
        print("All users were already OK.")
    
    return fixed

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planova.settings")
    django.setup()
    
    fix_all_users()
