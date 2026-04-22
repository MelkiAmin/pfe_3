"""
Database fix script to restore old user accounts.
Run with: python manage.py shell < fix_old_users.py
Or: python manage.py shell -c "exec(open('fix_old_users.py').read())"
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planova.settings')
django.setup()

from apps.accounts.models import User

def fix_old_users():
    print("=" * 50)
    print("FIXING OLD USER ACCOUNTS")
    print("=" * 50)
    
    # Get all users
    users = User.objects.all()
    fixed_count = 0
    
    for user in users:
        changes = []
        
        # Fix NULL role
        if not user.role or user.role == '':
            user.role = User.Role.ATTENDEE
            changes.append("role -> attendee")
        
        # Fix NULL/empty status
        if not user.status or user.status == '':
            user.status = User.Status.APPROVED
            changes.append("status -> approved")
        
        # Ensure is_active is True for non-banned users
        if not user.is_active and not user.ban_reason:
            user.is_active = True
            changes.append("is_active -> True")
        
        if changes:
            user.save(update_fields=['role', 'status', 'is_active', 'updated_at'])
            fixed_count += 1
            print(f"[+] {user.email}: {', '.join(changes)}")
    
    print("-" * 50)
    print(f"Total fixed: {fixed_count}/{users.count()} users")
    print("=" * 50)
    
    # Verify login works
    print("\nVerifying login for test accounts...")
    test_accounts = [
        ('admin@planova.com', 'admin123'),
        ('organisateur@planova.com', 'org123'),
        ('user@planova.com', 'user123'),
    ]
    
    for email, password in test_accounts:
        try:
            user = User.objects.get(email__iexact=email)
            if user.check_password(password):
                print(f"  [+] {email} - OK")
            else:
                print(f"  [-] {email} - PASSWORD MISMATCH")
        except User.DoesNotExist:
            print(f"  [-] {email} - NOT FOUND")

if __name__ == "__main__":
    fix_old_users()