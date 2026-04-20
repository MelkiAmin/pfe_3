import pytest
from rest_framework import status

from apps.accounts.models import User
from apps.events.models import Category, Event
from apps.notifications.models import Notification
from apps.tickets.models import TicketType


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email='org@test.com', password='OrgPass123!',
        first_name='Org', last_name='User', role=User.Role.ORGANIZER,
    )


@pytest.fixture
def attendee(db):
    return User.objects.create_user(
        email='att@test.com', password='AttPass123!',
        first_name='Att', last_name='User', role=User.Role.ATTENDEE,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(name='Music', slug='music')


@pytest.fixture
def event(db, organizer, category):
    return Event.objects.create(
        organizer=organizer,
        category=category,
        title='Rock Night',
        slug='rock-night',
        description='Live rock show',
        status=Event.Status.APPROVED,
        start_date='2026-08-01T20:00:00Z',
        end_date='2026-08-01T23:00:00Z',
        max_capacity=200,
    )


class TestEventList:
    def test_public_can_list_approved_events(self, api_client, event):
        resp = api_client.get('/api/events/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_search_by_title(self, api_client, event):
        resp = api_client.get('/api/events/?search=Rock')
        assert resp.status_code == status.HTTP_200_OK
        assert any('Rock' in e['title'] for e in resp.data['results'])

    def test_filter_by_category(self, api_client, event, category):
        resp = api_client.get(f'/api/events/?category={category.id}')
        assert resp.status_code == status.HTTP_200_OK


class TestEventCreate:
    def test_organizer_can_create_event(self, api_client, organizer, category, django_image):
        api_client.force_authenticate(user=organizer)
        resp = api_client.post('/api/events/', {
            'title': 'Jazz Festival',
            'description': 'Annual jazz festival',
            'category': category.id,
            'event_type': 'in_person',
            'cover_image': django_image,
            'ticket_price': '35.00',
            'ticket_quantity': 250,
            'start_date': '2026-09-15T18:00:00Z',
            'end_date': '2026-09-15T23:00:00Z',
            'city': 'Tunis',
            'country': 'Tunisia',
            'max_capacity': 500,
            'is_free': False,
        }, format='multipart')

        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['title'] == 'Jazz Festival'
        assert resp.data['status'] == Event.Status.PENDING
        assert TicketType.objects.filter(event_id=resp.data['id'], quantity=250).exists()

    def test_attendee_cannot_create_event(self, api_client, attendee, category):
        api_client.force_authenticate(user=attendee)
        resp = api_client.post('/api/events/', {
            'title': 'Fake Event',
            'description': 'x',
            'category': category.id,
            'event_type': 'online',
            'start_date': '2026-09-15T18:00:00Z',
            'end_date': '2026-09-15T23:00:00Z',
        }, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_event_creation_notifies_admin(self, api_client, organizer, category, django_image):
        admin = User.objects.create_user(
            email='admin@test.com',
            password='AdminPass123!',
            first_name='Admin',
            last_name='User',
            role=User.Role.ADMIN,
        )
        api_client.force_authenticate(user=organizer)
        resp = api_client.post('/api/events/', {
            'title': 'Pending Event',
            'description': 'Needs approval',
            'category': category.id,
            'event_type': 'in_person',
            'cover_image': django_image,
            'ticket_price': '15.00',
            'ticket_quantity': 40,
            'start_date': '2026-09-20T18:00:00Z',
            'end_date': '2026-09-20T22:00:00Z',
        }, format='multipart')

        assert resp.status_code == status.HTTP_201_CREATED
        assert Notification.objects.filter(
            recipient=admin,
            notification_type=Notification.Type.EVENT_SUBMITTED,
        ).exists()


class TestEventStatusWorkflow:
    def test_cancel_approved_event(self, api_client, organizer, event):
        api_client.force_authenticate(user=organizer)
        resp = api_client.post(f'/api/events/{event.id}/status/', {'action': 'cancel'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        event.refresh_from_db()
        assert event.status == Event.Status.CANCELLED

    def test_my_events_returns_organizer_events(self, api_client, organizer, event):
        api_client.force_authenticate(user=organizer)
        resp = api_client.get('/api/events/my-events/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1
