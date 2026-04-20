from django.db import migrations
from django.contrib.auth.hashers import make_password


def seed_default_accounts(apps, schema_editor):
    User = apps.get_model('accounts', 'User')

    default_accounts = [
        {
            'email': 'admin@planova.com',
            'password': 'admin123',
            'first_name': 'Planova',
            'last_name': 'Admin',
            'role': 'admin',
            'is_staff': True,
        },
        {
            'email': 'organisateur@planova.com',
            'password': 'org123',
            'first_name': 'Planova',
            'last_name': 'Organisateur',
            'role': 'organizer',
        },
        {
            'email': 'user@planova.com',
            'password': 'user123',
            'first_name': 'Planova',
            'last_name': 'Utilisateur',
            'role': 'attendee',
        },
    ]

    for account in default_accounts:
        email = account['email']
        password = account.pop('password')
        user, created = User.objects.get_or_create(email=email, defaults=account)
        if created:
            user.password = make_password(password)
            user.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_two_factor_fields'),
    ]

    operations = [
        migrations.RunPython(seed_default_accounts, migrations.RunPython.noop),
    ]
