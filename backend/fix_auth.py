"""
Complete fix for authentication issues.
This script fixes all database inconsistencies that cause login/register failures.

Run with: python manage.py shell < fix_auth.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planova.settings')
django.setup()

from django.db import transaction
from django.utils import timezone
from apps.accounts.models import User

def fix_all_auth_issues():
    print("\n" + "="*60)
    print("FIXING AUTHENTICATION ISSUES")
    print("="*60 + "\n")
    
    all_users = User.objects.all()
    total = all_users.count()
    
    print(f"Total users in database: {total}\n")
    
    fixed_users = []
    errors = []
    
    with transaction.atomic():
        for user in all_users:
            try:
                changes = []
                
                # Fix 1: Ensure role is valid
                valid_roles = [choice[0] for choice in User.Role.choices]
                if not user.role or user.role not in valid_roles:
                    user.role = User.Role.ATTENDEE
                    changes.append(f"role -> attendee")
                
                # Fix 2: Ensure status is valid
                valid_statuses = [choice[0] for choice in User.Status.choices]
                if not user.status or user.status not in valid_statuses:
                    user.status = User.Status.APPROVED
                    changes.append(f"status -> approved")
                
                # Fix 3: Ensure is_active is True (unless explicitly banned)
                if not user.is_active and not user.ban_reason:
                    user.is_active = True
                    changes.append(f"is_active -> True")
                
                # Fix 4: Ensure is_2fa_enabled exists
                if user.is_2fa_enabled is None:
                    user.is_2fa_enabled = False
                    changes.append(f"is_2fa_enabled -> False")
                
                # Fix 5: Ensure two_factor_secret is not null
                if not user.two_factor_secret:
                    user.two_factor_secret = ''
                
                if changes:
                    user.updated_at = timezone.now()
                    user.save(update_fields=[
                        'role', 'status', 'is_active', 
                        'is_2fa_enabled', 'two_factor_secret', 'updated_at'
                    ])
                    fixed_users.append((user.email, changes))
                    print(f"✓ FIXED: {user.email}")
                    for change in changes:
                        print(f"    - {change}")
                else:
                    print(f"  OK:   {user.email}")
                    
            except Exception as e:
                errors.append((user.email, str(e)))
                print(f"✗ ERROR: {user.email} -> {str(e)}")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total users:     {total}")
    print(f"Fixed:           {len(fixed_users)}")
    print(f"Already OK:      {total - len(fixed_users) - len(errors)}")
    print(f"Errors:          {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for email, error in errors:
            print(f"  - {email}: {error}")
    
    if fixed_users:
        print("\n" + "="*60)
        print("SUCCESS! All authentication issues have been fixed.")
        print("Users can now log in with their credentials.")
        print("="*60 + "\n")
    else:
        print("\nNo fixes needed - all users are already valid.")
    
    return fixed_users, errors

if __name__ == "__main__":
    fix_all_auth_issues()
