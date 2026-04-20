from django.db import migrations
from django.contrib.auth.hashers import make_password


def fix_seeded_users(apps, schema_editor):
    User = apps.get_model('accounts', 'User')

    default_accounts = [
        {
            'email': 'admin@planova.com',
            'password': 'admin123',
            'first_name': 'Planova',
            'last_name': 'Admin',
            'role': 'admin',
            'is_staff': True,
            'is_email_verified': True,
            'approval_status': 'approved',
        },
        {
            'email': 'organisateur@planova.com',
            'password': 'org123',
            'first_name': 'Planova',
            'last_name': 'Organisateur',
            'role': 'organizer',
            'is_email_verified': True,
            'approval_status': 'approved',
        },
        {
            'email': 'user@planova.com',
            'password': 'user123',
            'first_name': 'Planova',
            'last_name': 'Utilisateur',
            'role': 'attendee',
            'is_email_verified': True,
            'approval_status': 'approved',
        },
    ]

    for account in default_accounts:
        email = account['email']
        password = account.pop('password')

        try:
            user = User.objects.get(email=email)
            user.password = make_password(password)
            user.is_email_verified = True
            user.approval_status = account.get('approval_status', 'approved')
            user.is_active = True
            user.save(update_fields=['password', 'is_email_verified', 'approval_status', 'is_active'])
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=account['first_name'],
                last_name=account['last_name'],
                role=account['role'],
                is_staff=account.get('is_staff', False),
                is_email_verified=True,
                approval_status=account.get('approval_status', 'approved'),
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_add_approval_fields'),
    ]

    operations = [
        migrations.RunPython(fix_seeded_users, noop),
    ]