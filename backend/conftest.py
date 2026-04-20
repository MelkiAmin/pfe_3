from datetime import timedelta
from decimal import Decimal
import itertools

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.events.models import Category, Event
from apps.payments.models import Payment
from apps.tickets.models import TicketType


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    counter = itertools.count(1)
    User = get_user_model()

    def create_user(**kwargs):
        index = next(counter)
        password = kwargs.pop('password', 'StrongPass123!')
        defaults = {
            'email': f'user{index}@example.com',
            'first_name': 'Test',
            'last_name': f'User{index}',
            'role': User.Role.ATTENDEE,
        }
        defaults.update(kwargs)
        user = User.objects.create_user(password=password, **defaults)
        user.raw_password = password
        return user

    return create_user


@pytest.fixture
def auth_headers_for():
    def make_headers(user):
        token = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token.access_token}'}
    return make_headers


@pytest.fixture
def organizer_user(db, user_factory):
    return user_factory(role='organizer', email='organizer@test.com')


@pytest.fixture
def admin_user(db, user_factory):
    User = get_user_model()
    return User.objects.create_user(
        email='admin@test.com', password='AdminPass123!',
        first_name='Admin', last_name='User',
        role=User.Role.ADMIN, is_staff=True,
    )


@pytest.fixture
def attendee_user(db, user_factory):
    return user_factory(role='attendee', email='attendee@test.com')


@pytest.fixture
def event_factory(db, user_factory):
    category_counter = itertools.count(1)
    event_counter    = itertools.count(1)

    def create_event(**kwargs):
        organizer = kwargs.pop('organizer', user_factory(role='organizer'))
        cat_idx   = next(category_counter)
        category  = kwargs.pop(
            'category',
            Category.objects.create(name=f'Category {cat_idx}', slug=f'category-{cat_idx}'),
        )
        ev_idx     = next(event_counter)
        start_date = kwargs.pop('start_date', timezone.now() + timedelta(days=7))
        end_date   = kwargs.pop('end_date',   start_date + timedelta(hours=3))
        defaults   = {
            'organizer':   organizer,
            'category':    category,
            'title':       f'Event {ev_idx}',
            'slug':        f'event-{ev_idx}',
            'description': 'Test event description',
            'status':      Event.Status.APPROVED,
            'event_type':  Event.EventType.IN_PERSON,
            'start_date':  start_date,
            'end_date':    end_date,
            'venue_name':  'Main Hall',
            'city':        'Tunis',
            'country':     'Tunisia',
            'max_capacity': 100,
        }
        defaults.update(kwargs)
        return Event.objects.create(**defaults)

    return create_event


@pytest.fixture
def ticket_type_factory(db):
    def create_ticket_type(event, **kwargs):
        defaults = {
            'event':         event,
            'name':          'General Admission',
            'description':   'Standard access pass',
            'price':         Decimal('49.99'),
            'quantity':      50,
            'quantity_sold': 0,
        }
        defaults.update(kwargs)
        return TicketType.objects.create(**defaults)
    return create_ticket_type


@pytest.fixture
def payment_factory(db):
    def create_payment(user, event, **kwargs):
        defaults = {
            'user':               user,
            'event':              event,
            'amount':             Decimal('99.98'),
            'currency':           'USD',
            'status':             Payment.Status.PENDING,
            'provider':           Payment.Provider.STRIPE,
            'provider_session_id':'cs_test_default',
            'metadata':           {},
        }
        defaults.update(kwargs)
        return Payment.objects.create(**defaults)
    return create_payment


@pytest.fixture
def django_image():
    return SimpleUploadedFile(
        'cover.jpg',
        (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
            b'\xff\xdb\x00C\x00'
            + b'\x08' * 64
            + b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01'
            + b'\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xd2\xcf \xff\xd9'
        ),
        content_type='image/jpeg',
    )
