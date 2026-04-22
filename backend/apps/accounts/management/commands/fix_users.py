from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Fix existing user accounts to restore login access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        users = User.objects.all()
        fixed_count = 0
        already_ok_count = 0
        
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=== Fixing User Accounts ==='))
        self.stdout.write('')
        
        for user in users:
            changes = []
            
            # Fix is_active if needed
            if not user.is_active:
                # Check if user was explicitly banned
                if user.ban_reason:
                    changes.append(f"is_active={user.is_active} (BANNED: {user.ban_reason[:30]}...)")
                else:
                    changes.append(f"is_active={user.is_active} → True (restoring)")
                    if not dry_run:
                        user.is_active = True
            
            # Fix status if needed
            if user.status == User.Status.PENDING:
                # Check if user has been active before (has logins, events, etc.)
                # For backward compatibility, approve all pending users
                changes.append(f"status={user.status} → approved")
                if not dry_run:
                    user.status = User.Status.APPROVED
            
            # Fix role if needed
            if not user.role:
                changes.append(f"role={user.role} → attendee (default)")
                if not dry_run:
                    user.role = User.Role.ATTENDEE
            
            if changes:
                if not dry_run:
                    user.updated_at = timezone.now()
                    user.save()
                
                self.stdout.write(self.style.SUCCESS(f"✓ {user.email}"))
                for change in changes:
                    self.stdout.write(f"    {change}")
                fixed_count += 1
            else:
                already_ok_count += 1
        
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('=== Summary ==='))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"DRY RUN - No changes made"))
            self.stdout.write('')
        
        self.stdout.write(f"Total users: {users.count()}")
        self.stdout.write(self.style.SUCCESS(f"Fixed: {fixed_count}"))
        self.stdout.write(self.style.INFO(f"Already OK: {already_ok_count}"))
        
        if not dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS("All user accounts have been fixed!"))
            self.stdout.write("Users can now log in with their existing credentials.")
        
        return
