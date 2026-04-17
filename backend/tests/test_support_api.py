import pytest
from rest_framework import status
from apps.accounts.models import User
from apps.support.models import SupportTicket

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='support_user@test.com', password='Pass123!',
        first_name='S', last_name='User', role=User.Role.ATTENDEE
    )

@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email='support_admin@test.com', password='AdminPass123!',
        first_name='A', last_name='Admin', role=User.Role.ADMIN, is_staff=True
    )

class TestSupportTickets:
    def test_user_creates_ticket(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.post('/api/support/tickets/', {
            'subject': 'Cannot access my ticket',
            'description': 'I paid but the ticket is not showing in my dashboard.',
            'priority': 'high',
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['status'] == 'open'
        assert 'ticket_ref' in resp.data

    def test_user_lists_own_tickets(self, api_client, user):
        api_client.force_authenticate(user=user)
        SupportTicket.objects.create(user=user, subject='Test', description='Test')
        resp = api_client.get('/api/support/tickets/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_admin_sees_all_tickets(self, api_client, admin, user):
        SupportTicket.objects.create(user=user, subject='Test', description='Help')
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/support/admin/tickets/')
        assert resp.status_code == status.HTTP_200_OK

    def test_admin_replies_and_changes_status(self, api_client, admin, user):
        ticket = SupportTicket.objects.create(user=user, subject='Issue', description='Problem')
        api_client.force_authenticate(user=admin)
        resp = api_client.post(f'/api/support/admin/tickets/{ticket.id}/reply/', {
            'message': 'We are looking into this.',
            'status': 'in_review',
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        ticket.refresh_from_db()
        assert ticket.status == SupportTicket.Status.IN_REVIEW
        assert ticket.messages.count() == 1

    def test_user_adds_message_to_own_ticket(self, api_client, user):
        ticket = SupportTicket.objects.create(user=user, subject='Issue', description='Problem')
        api_client.force_authenticate(user=user)
        resp = api_client.post(f'/api/support/tickets/{ticket.id}/message/', {
            'message': 'Any update on this?'
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
