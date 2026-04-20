import pytest
from decimal import Decimal
from rest_framework import status
from apps.accounts.models import User
from apps.events.models import Event, Category
from apps.tickets.models import Ticket, TicketType


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        email='org@tickets.com', password='Org123!',
        first_name='O', last_name='U', role=User.Role.ORGANIZER,
    )

@pytest.fixture
def attendee(db):
    return User.objects.create_user(
        email='att@tickets.com', password='Att123!',
        first_name='A', last_name='U', role=User.Role.ATTENDEE,
    )

@pytest.fixture
def category(db):
    return Category.objects.create(name='Festival', slug='festival')

@pytest.fixture
def event(db, organizer, category):
    return Event.objects.create(
        organizer=organizer, category=category,
        title='Summer Fest', slug='summer-fest',
        description='Big festival',
        status=Event.Status.APPROVED,
        start_date='2026-07-15T14:00:00Z',
        end_date='2026-07-15T23:00:00Z',
        max_capacity=500,
    )

@pytest.fixture
def ticket_type(db, event):
    return TicketType.objects.create(
        event=event, name='VIP', description='VIP access',
        price=Decimal('99.00'), quantity=50, quantity_sold=0,
    )

@pytest.fixture
def confirmed_ticket(db, ticket_type, event, attendee):
    return Ticket.objects.create(
        ticket_type=ticket_type, event=event, attendee=attendee,
        status=Ticket.Status.CONFIRMED, price_paid=Decimal('99.00'),
    )


class TestTicketTypes:
    def test_public_can_list_ticket_types(self, api_client, ticket_type):
        resp = api_client.get('/api/tickets/types/')
        assert resp.status_code == status.HTTP_200_OK

    def test_organizer_creates_ticket_type(self, api_client, organizer, event):
        api_client.force_authenticate(user=organizer)
        resp = api_client.post('/api/tickets/types/', {
            'event': event.id, 'name': 'Early Bird',
            'description': 'Early bird discount',
            'price': '29.99', 'quantity': 100,
        }, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data['name'] == 'Early Bird'

    def test_attendee_cannot_create_ticket_type(self, api_client, attendee, event):
        api_client.force_authenticate(user=attendee)
        resp = api_client.post('/api/tickets/types/', {
            'event': event.id, 'name': 'Fake', 'price': '0', 'quantity': 1,
        }, format='json')
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestTicketCheckIn:
    def test_organizer_can_check_in_ticket(self, api_client, organizer, confirmed_ticket):
        api_client.force_authenticate(user=organizer)
        resp = api_client.post(f'/api/tickets/{confirmed_ticket.id}/check_in/')
        assert resp.status_code == status.HTTP_200_OK
        confirmed_ticket.refresh_from_db()
        assert confirmed_ticket.status == Ticket.Status.USED
        assert confirmed_ticket.checked_in_at is not None

    def test_cannot_check_in_already_used_ticket(self, api_client, organizer, confirmed_ticket):
        confirmed_ticket.status = Ticket.Status.USED
        confirmed_ticket.save()
        api_client.force_authenticate(user=organizer)
        resp = api_client.post(f'/api/tickets/{confirmed_ticket.id}/check_in/')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_attendee_can_list_own_tickets(self, api_client, attendee, confirmed_ticket):
        api_client.force_authenticate(user=attendee)
        resp = api_client.get('/api/tickets/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] >= 1

    def test_attendee_cannot_see_others_tickets(self, api_client, attendee, organizer, ticket_type, event):
        other = User.objects.create_user(
            email='other@test.com', password='P123!',
            first_name='O', last_name='T', role=User.Role.ATTENDEE,
        )
        Ticket.objects.create(
            ticket_type=ticket_type, event=event, attendee=other,
            status=Ticket.Status.CONFIRMED, price_paid=Decimal('99.00'),
        )
        api_client.force_authenticate(user=attendee)
        resp = api_client.get('/api/tickets/')
        # attendee has 0 tickets
        assert resp.data['count'] == 0
