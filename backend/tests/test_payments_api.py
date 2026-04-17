from types import SimpleNamespace

import pytest

from apps.payments.models import Payment
from apps.tickets.models import Ticket


@pytest.mark.django_db
def test_create_checkout_session_creates_pending_payment(
    api_client,
    user_factory,
    auth_headers_for,
    event_factory,
    ticket_type_factory,
    monkeypatch,
):
    user = user_factory()
    event = event_factory()
    ticket_type = ticket_type_factory(event, price='25.00', quantity=20)
    api_client.credentials(**auth_headers_for(user))

    fake_session = SimpleNamespace(id='cs_test_123', url='https://checkout.stripe.test/session')
    fake_client = SimpleNamespace(
        checkout=SimpleNamespace(
            Session=SimpleNamespace(create=lambda **kwargs: fake_session),
        ),
    )
    monkeypatch.setattr('apps.payments.views.get_stripe', lambda: fake_client)

    response = api_client.post(
        '/api/payments/checkout/',
        {
            'ticket_type_id': ticket_type.id,
            'quantity': 2,
            'success_url': 'https://example.com/success',
            'cancel_url': 'https://example.com/cancel',
        },
        format='json',
    )

    assert response.status_code == 200
    payment = Payment.objects.get(provider_session_id='cs_test_123')
    assert payment.user == user
    assert payment.status == Payment.Status.PENDING
    assert response.data['payment_id'] == payment.id


@pytest.mark.django_db
def test_confirm_payment_marks_payment_complete_and_creates_tickets(
    api_client,
    user_factory,
    auth_headers_for,
    event_factory,
    ticket_type_factory,
    payment_factory,
    monkeypatch,
):
    user = user_factory()
    event = event_factory()
    ticket_type = ticket_type_factory(event, price='25.00', quantity=20)
    payment = payment_factory(
        user,
        event,
        amount='50.00',
        provider_session_id='cs_paid_123',
        metadata={'ticket_type_id': str(ticket_type.id), 'quantity': '2'},
    )
    api_client.credentials(**auth_headers_for(user))

    fake_session = {
        'id': 'cs_paid_123',
        'status': 'complete',
        'payment_status': 'paid',
        'payment_intent': 'pi_123',
        'metadata': {'ticket_type_id': str(ticket_type.id), 'quantity': '2'},
    }
    fake_client = SimpleNamespace(
        checkout=SimpleNamespace(
            Session=SimpleNamespace(retrieve=lambda session_id: fake_session),
        ),
    )
    monkeypatch.setattr('apps.payments.views.get_stripe', lambda: fake_client)
    monkeypatch.setattr('apps.notifications.tasks.send_order_confirmation_email.delay', lambda payment_id: None)
    monkeypatch.setattr('apps.tickets.models.Ticket.attach_qr_code', lambda self, save=True: None)

    response = api_client.post(
        '/api/payments/confirm/',
        {'session_id': payment.provider_session_id},
        format='json',
    )

    payment.refresh_from_db()
    ticket_type.refresh_from_db()

    assert response.status_code == 200
    assert response.data['fulfilled'] is True
    assert payment.status == Payment.Status.COMPLETED
    assert Ticket.objects.filter(event=event, attendee=user).count() == 2
    assert ticket_type.quantity_sold == 2


@pytest.mark.django_db
def test_stripe_webhook_marks_expired_payment_failed(
    api_client,
    user_factory,
    event_factory,
    payment_factory,
    monkeypatch,
):
    user = user_factory()
    event = event_factory()
    payment = payment_factory(user, event, provider_session_id='cs_expired_123')

    fake_event = {
        'type': 'checkout.session.expired',
        'data': {
            'object': {
                'id': 'cs_expired_123',
                'status': 'expired',
                'payment_status': 'unpaid',
            },
        },
    }
    fake_client = SimpleNamespace(
        Webhook=SimpleNamespace(construct_event=lambda payload, sig_header, secret: fake_event),
    )
    monkeypatch.setattr('apps.payments.views.get_stripe', lambda: fake_client)

    response = api_client.post(
        '/api/payments/webhook/stripe/',
        data=b'{}',
        content_type='application/json',
        HTTP_STRIPE_SIGNATURE='test-signature',
    )

    payment.refresh_from_db()
    assert response.status_code == 200
    assert payment.status == Payment.Status.FAILED
