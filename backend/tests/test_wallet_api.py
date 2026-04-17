import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.payments.models import Wallet, Transaction, WithdrawalRequest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def attendee(db):
    return User.objects.create_user(
        email='attendee@test.com',
        password='TestPass123!',
        first_name='Test',
        last_name='User',
        role=User.Role.ATTENDEE,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User',
        role=User.Role.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def auth_client(api_client, attendee):
    api_client.force_authenticate(user=attendee)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


class TestWallet:
    def test_get_wallet_creates_if_not_exists(self, auth_client):
        response = auth_client.get('/api/payments/wallet/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['balance'] == '0.00'

    def test_get_wallet_returns_balance(self, auth_client, attendee):
        Wallet.objects.create(user=attendee, balance=Decimal('50.00'))
        response = auth_client.get('/api/payments/wallet/')
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['balance']) == Decimal('50.00')

    def test_unauthenticated_cannot_access_wallet(self, api_client):
        response = api_client.get('/api/payments/wallet/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTransactions:
    def test_list_transactions_empty(self, auth_client):
        response = auth_client.get('/api/payments/transactions/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_list_own_transactions_only(self, auth_client, attendee, admin_user):
        Transaction.objects.create(
            user=attendee, amount=Decimal('10'), trx_type='credit',
            details='Test credit', post_balance=Decimal('10')
        )
        Transaction.objects.create(
            user=admin_user, amount=Decimal('20'), trx_type='credit',
            details='Admin credit', post_balance=Decimal('20')
        )
        response = auth_client.get('/api/payments/transactions/')
        assert response.data['count'] == 1


class TestWithdrawalRequest:
    def test_create_withdrawal_insufficient_balance(self, auth_client, attendee):
        Wallet.objects.create(user=attendee, balance=Decimal('5.00'))
        response = auth_client.post('/api/payments/withdrawals/', {
            'amount': '100.00',
            'method': 'bank_transfer',
            'account_details': {'iban': 'TN59...' },
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_withdrawal_success(self, auth_client, attendee):
        Wallet.objects.create(user=attendee, balance=Decimal('200.00'))
        response = auth_client.post('/api/payments/withdrawals/', {
            'amount': '50.00',
            'method': 'bank_transfer',
            'account_details': {'iban': 'TN5901234567890'},
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'pending'

    def test_admin_approve_withdrawal(self, auth_client, admin_client, attendee):
        wallet = Wallet.objects.create(user=attendee, balance=Decimal('200.00'))
        wr = WithdrawalRequest.objects.create(
            user=attendee, amount=Decimal('50.00'),
            method='bank_transfer', account_details={}
        )
        response = admin_client.post(
            f'/api/payments/admin/withdrawals/{wr.pk}/action/',
            {'action': 'approve'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'approved'
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('150.00')
