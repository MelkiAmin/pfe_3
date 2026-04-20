#!/usr/bin/env python
"""
Script pour vérifier et recréer les comptes par défaut.
Usage: python manage.py shell < fix_accounts.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planova.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.accounts.models import User

def check_and_fix_accounts():
    accounts = [
        {
            'email': 'admin@planova.com',
            'password': 'admin123',
            'first_name': 'Planova',
            'last_name': 'Admin',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
            'is_email_verified': True,
            'approval_status': 'approved',
        },
        {
            'email': 'organisateur@planova.com',
            'password': 'org123',
            'first_name': 'Planova',
            'last_name': 'Organisateur',
            'role': 'organizer',
            'is_staff': False,
            'is_superuser': False,
            'is_email_verified': True,
            'approval_status': 'approved',
        },
        {
            'email': 'user@planova.com',
            'password': 'user123',
            'first_name': 'Planova',
            'last_name': 'Utilisateur',
            'role': 'attendee',
            'is_staff': False,
            'is_superuser': False,
            'is_email_verified': True,
            'approval_status': 'approved',
        },
    ]

    print("=" * 60)
    print("VÉRIFICATION ET CRÉATION DES COMPTES")
    print("=" * 60)

    for account in accounts:
        email = account['email']
        password = account.pop('password')

        try:
            user = User.objects.get(email__iexact=email)
            print(f"\n[EXISTE] {email}")

            # Update password
            user.set_password(password)
            user.first_name = account['first_name']
            user.last_name = account['last_name']
            user.role = account['role']
            user.is_staff = account['is_staff']
            user.is_superuser = account['is_superuser']
            user.is_email_verified = account['is_email_verified']
            user.approval_status = account['approval_status']
            user.is_active = True
            user.save()

            print(f"  └── Mot de passe: réinitialisé")
            print(f"  └── is_active: {user.is_active}")
            print(f"  └── is_staff: {user.is_staff}")
            print(f"  └── is_superuser: {user.is_superuser}")
            print(f"  └── role: {user.role}")
            print(f"  └── is_email_verified: {user.is_email_verified}")
            print(f"  └── approval_status: {user.approval_status}")

            # Verify password
            if user.check_password(password):
                print(f"  └── Password check: OK ✓")
            else:
                print(f"  └── Password check: ÉCHEC ✗")

        except User.DoesNotExist:
            print(f"\n[CRÉATION] {email}")

            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=account['first_name'],
                last_name=account['last_name'],
                role=account['role'],
                is_staff=account['is_staff'],
                is_superuser=account['is_superuser'],
                is_email_verified=account['is_email_verified'],
                approval_status=account['approval_status'],
            )

            print(f"  └── Utilisateur créé avec succes!")
            print(f"  └── is_active: {user.is_active}")
            print(f"  └── role: {user.role}")
            print(f"  └── is_email_verified: {user.is_email_verified}")
            print(f"  └── approval_status: {user.approval_status}")

            if user.check_password(password):
                print(f"  └── Password check: OK ✓")
            else:
                print(f"  └── Password check: ÉCHEC ✗")

    print("\n" + "=" * 60)
    print("RÉSUMÉ - Tous les comptes sont maintenant configurés:")
    print("=" * 60)

    for account in accounts:
        email = account['email']
        user = User.objects.get(email__iexact=email)
        print(f"  • {email} ({user.role}) - {user.first_name} {user.last_name}")
        print(f"    Password OK: {user.check_password(account['password'])}")

    print("\n" + "=" * 60)
    print("COMPTES CRÉÉS AVEC SUCCÈS!")
    print("=" * 60)
    print("\nVous pouvez maintenant vous connecter:")
    print("  Admin:     admin@planova.com / admin123")
    print("  Organizer: organisateur@planova.com / org123")
    print("  User:     user@planova.com / user123")
    print()

if __name__ == '__main__':
    check_and_fix_accounts()