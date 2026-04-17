from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.events.models import Category, Event
from apps.tickets.models import Ticket, TicketType


@override_settings(MEDIA_ROOT='/tmp/planova-test-media')
class TicketModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='ticket-owner@example.com',
            password='StrongPass123!',
            first_name='Ticket',
            last_name='Owner',
            role='attendee',
        )
        organizer = get_user_model().objects.create_user(
            email='organizer@example.com',
            password='StrongPass123!',
            first_name='Event',
            last_name='Organizer',
            role='organizer',
        )
        category = Category.objects.create(name='Concert', slug='concert')
        start_date = timezone.now() + timedelta(days=5)
        self.event = Event.objects.create(
            organizer=organizer,
            category=category,
            title='Ticketed Event',
            slug='ticketed-event',
            description='An event for testing tickets.',
            status=Event.Status.PUBLISHED,
            event_type=Event.EventType.IN_PERSON,
            start_date=start_date,
            end_date=start_date + timedelta(hours=2),
        )
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='VIP',
            price='99.99',
            quantity=10,
        )

    def test_attach_qr_code_generates_image_path(self):
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            event=self.event,
            attendee=self.user,
            status=Ticket.Status.CONFIRMED,
            price_paid='99.99',
        )

        ticket.attach_qr_code()

        self.assertTrue(ticket.qr_code.name.startswith('tickets/qr/ticket_'))
        self.assertIn(str(ticket.ticket_number), ticket.build_qr_payload())
