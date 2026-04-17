import pytest
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.events.models import Event, Category
from apps.tickets.models import Ticket, TicketType


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email='organizer@test.com',
        password='OrgPass123!',
        first_name='Org',
        last_name='User',
        role=User.Role.ORGANIZER,
    )


@pytest.fixture
def org_client(api_client, organizer):
    api_client.force_authenticate(user=organizer)
    return api_client


@pytest.fixture
def category(db):
    return Category.objects.create(name='Concert', slug='concert')


class TestOrganizerDashboard:
    def test_dashboard_unauthenticated(self, api_client):
        response = api_client.get('/api/organizer/dashboard/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_returns_metrics(self, org_client, organizer, category):
        event = Event.objects.create(
            organizer=organizer,
            category=category,
            title='Test Event',
            slug='test-event',
            description='A test event',
            status=Event.Status.PUBLISHED,
            start_date='2026-06-01T18:00:00Z',
            end_date='2026-06-01T22:00:00Z',
            max_capacity=100,
        )
        response = org_client.get('/api/organizer/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['total_events'] == 1
        assert data['published_events'] == 1
        assert 'total_revenue' in data
        assert 'top_events' in data
        assert 'recent_events' in data
        assert 'avg_fill_rate' in data
