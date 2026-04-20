import pytest
from decimal import Decimal
from rest_framework import status
from apps.accounts.models import User
from apps.events.models import Event, Category
from apps.payments.models import Payment
from apps.tickets.models import Ticket, TicketType


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email='admin@hotelmate.com', password='Admin123!',
        first_name='Admin', last_name='User',
        role=User.Role.ADMIN, is_staff=True,
    )

@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email='org@hotelmate.com', password='Org123!',
        first_name='Org', last_name='User', role=User.Role.ORGANIZER,
    )

@pytest.fixture
def category(db):
    return Category.objects.create(name='Tech', slug='tech')

@pytest.fixture
def event(db, organizer, category):
    return Event.objects.create(
        organizer=organizer, category=category,
        title='Tech Summit', slug='tech-summit',
        description='Annual tech summit',
        status=Event.Status.PENDING,
        start_date='2026-10-01T09:00:00Z',
        end_date='2026-10-01T18:00:00Z',
    )


class TestAdminDashboard:
    def test_admin_dashboard_returns_metrics(self, api_client, admin):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/admin-panel/dashboard/')
        assert resp.status_code == status.HTTP_200_OK
        assert 'total_users' in resp.data
        assert 'total_revenue' in resp.data

    def test_non_admin_forbidden(self, api_client, organizer):
        api_client.force_authenticate(user=organizer)
        resp = api_client.get('/api/admin-panel/dashboard/')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_system_stats(self, api_client, admin):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/admin-panel/stats/')
        assert resp.status_code == status.HTTP_200_OK
        for key in ['total_users', 'pending_withdrawals', 'open_support_tickets', 'pending_kyc']:
            assert key in resp.data


class TestAdminEventModeration:
    def test_approve_event(self, api_client, admin, event):
        api_client.force_authenticate(user=admin)
        resp = api_client.post(
            f'/api/admin-panel/events/{event.id}/moderate/',
            {'action': 'approve'}, format='json'
        )
        assert resp.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.status == Event.Status.APPROVED

    def test_reject_event_with_reason(self, api_client, admin, event):
        api_client.force_authenticate(user=admin)
        resp = api_client.post(
            f'/api/admin-panel/events/{event.id}/moderate/',
            {'action': 'reject', 'reason': 'Incomplete information'}, format='json'
        )
        assert resp.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.status == Event.Status.REJECTED

    def test_invalid_action_returns_400(self, api_client, admin, event):
        api_client.force_authenticate(user=admin)
        resp = api_client.post(
            f'/api/admin-panel/events/{event.id}/moderate/',
            {'action': 'invalid'}, format='json'
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


class TestAdminUserManagement:
    def test_admin_lists_users(self, api_client, admin):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/admin-panel/users/')
        assert resp.status_code == status.HTTP_200_OK

    def test_admin_searches_users(self, api_client, admin, organizer):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/admin-panel/users/?search=org@hotelmate')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_admin_deletes_user(self, api_client, admin, db):
        target = User.objects.create_user(
            email='delete@me.com', password='Pass123!',
            first_name='D', last_name='U', role=User.Role.ATTENDEE
        )
        api_client.force_authenticate(user=admin)
        resp = api_client.delete(f'/api/admin-panel/users/{target.id}/')
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=target.id).exists()


class TestAdminRevenueReport:
    def test_download_csv(self, api_client, admin):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/admin-panel/reports/revenue/')
        assert resp.status_code == status.HTTP_200_OK
        assert 'text/csv' in resp['Content-Type']
        assert 'attachment' in resp['Content-Disposition']
