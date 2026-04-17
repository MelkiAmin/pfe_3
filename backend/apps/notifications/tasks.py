import json
from datetime import timedelta
from urllib import error, request

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone


SENDGRID_API_URL = 'https://api.sendgrid.com/v3/mail/send'


def send_sendgrid_email(to_email, subject, text_content, html_content=None):
    if not settings.SENDGRID_API_KEY:
        raise RuntimeError('SENDGRID_API_KEY is not configured.')

    payload = {
        'personalizations': [
            {
                'to': [{'email': to_email}],
                'subject': subject,
            },
        ],
        'from': {'email': settings.SENDGRID_FROM_EMAIL},
        'content': [
            {'type': 'text/plain', 'value': text_content},
        ],
    }

    if html_content:
        payload['content'].append({'type': 'text/html', 'value': html_content})

    http_request = request.Request(
        SENDGRID_API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    timeout = getattr(settings, 'SENDGRID_TIMEOUT', 10)

    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            if response.status >= 400:
                raise RuntimeError(f'SendGrid returned status {response.status}')
    except error.HTTPError as exc:
        details = exc.read().decode('utf-8', errors='ignore')
        raise RuntimeError(f'SendGrid HTTP error {exc.code}: {details}') from exc
    except error.URLError as exc:
        raise RuntimeError(f'SendGrid connection error: {exc.reason}') from exc


def send_templated_sendgrid_email(to_email, subject, text_template, html_template, context):
    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)
    send_sendgrid_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    )


@shared_task(bind=True, autoretry_for=(RuntimeError,), retry_backoff=True, max_retries=3)
def send_order_confirmation_email(self, payment_id):
    from apps.payments.models import Payment

    payment = (
        Payment.objects.select_related('event', 'user')
        .prefetch_related('user__tickets', 'event__tickets')
        .get(pk=payment_id)
    )
    tickets = list(
        payment.user.tickets.filter(
            event=payment.event,
            status__in=['confirmed', 'used'],
        ).order_by('created_at')
    )

    context = {
        'user': payment.user,
        'event': payment.event,
        'payment': payment,
        'tickets': tickets,
        'ticket_count': len(tickets),
    }

    send_templated_sendgrid_email(
        to_email=payment.user.email,
        subject=f'Order confirmed for {payment.event.title}',
        text_template='emails/order_confirmation.txt',
        html_template='emails/order_confirmation.html',
        context=context,
    )


@shared_task(bind=True, autoretry_for=(RuntimeError,), retry_backoff=True, max_retries=3)
def send_event_reminder_email(self, user_id, event_id, ticket_ids):
    from apps.accounts.models import User
    from apps.events.models import Event
    from apps.tickets.models import Ticket

    user = User.objects.get(pk=user_id)
    event = Event.objects.get(pk=event_id)
    tickets = list(Ticket.objects.filter(pk__in=ticket_ids).order_by('created_at'))

    context = {
        'user': user,
        'event': event,
        'tickets': tickets,
    }

    send_templated_sendgrid_email(
        to_email=user.email,
        subject=f'Reminder: {event.title} starts soon',
        text_template='emails/event_reminder.txt',
        html_template='emails/event_reminder.html',
        context=context,
    )

@shared_task
def send_event_cancellation_email(user_email, event_title):
    send_sendgrid_email(
        to_email=user_email,
        subject=f'Event Cancelled – {event_title}',
        text_content=f'"{event_title}" has been cancelled. A refund will be processed shortly.',
    )


@shared_task
def queue_event_reminder_emails():
    from apps.events.models import Event
    from apps.notifications.models import Notification
    from apps.tickets.models import Ticket

    reminder_window_start = timezone.now() + timedelta(hours=23)
    reminder_window_end = timezone.now() + timedelta(hours=25)

    events = Event.objects.filter(
        status=Event.Status.PUBLISHED,
        start_date__gte=reminder_window_start,
        start_date__lte=reminder_window_end,
    )

    for event in events:
        tickets = (
            Ticket.objects.filter(
                event=event,
                status__in=[Ticket.Status.CONFIRMED, Ticket.Status.USED],
            )
            .select_related('attendee')
            .order_by('attendee_id', 'created_at')
        )

        attendee_ticket_map = {}
        for ticket in tickets:
            attendee_ticket_map.setdefault(ticket.attendee_id, []).append(ticket)

        for attendee_id, attendee_tickets in attendee_ticket_map.items():
            attendee = attendee_tickets[0].attendee
            reminder_key = f'event-reminder:{event.id}:{attendee.id}'
            already_sent = Notification.objects.filter(
                recipient=attendee,
                notification_type=Notification.Type.EVENT_REMINDER,
                data__reminder_key=reminder_key,
            ).exists()

            if already_sent:
                continue

            send_event_reminder_email.delay(
                attendee.id,
                event.id,
                [ticket.id for ticket in attendee_tickets],
            )
            create_notification(
                recipient=attendee,
                notification_type=Notification.Type.EVENT_REMINDER,
                title=f'Reminder: {event.title} starts soon',
                message=f'Don\'t forget, {event.title} starts on {event.start_date}.',
                data={
                    'event_id': event.id,
                    'ticket_ids': [ticket.id for ticket in attendee_tickets],
                    'reminder_key': reminder_key,
                },
            )


def create_notification(recipient, notification_type, title, message, data=None):
    from .models import Notification
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        data=data or {},
    )


# ─── SMS via Twilio (opt-in) ─────────────────────────────────────────────────

def send_sms(to_number: str, message: str) -> bool:
    """
    Send an SMS via Twilio. Requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER to be set in settings/env.
    Falls back silently if credentials are missing (dev/test mode).
    """
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    auth_token  = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', '')

    if not all([account_sid, auth_token, from_number]):
        import logging
        logging.getLogger(__name__).debug('Twilio not configured — SMS skipped: %s', message)
        return False

    try:
        from twilio.rest import Client  # type: ignore
        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=to_number)
        return True
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error('Twilio SMS error: %s', exc)
        return False


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def send_ticket_purchase_sms(self, phone: str, event_title: str, ticket_count: int):
    """Send SMS confirmation after ticket purchase."""
    msg = f'HotelMate: You have {ticket_count} ticket(s) for "{event_title}". Enjoy the event!'
    send_sms(phone, msg)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def send_event_reminder_sms(self, phone: str, event_title: str, start_date: str):
    """Send SMS reminder 24h before event."""
    msg = f'HotelMate Reminder: "{event_title}" starts tomorrow at {start_date}. See you there!'
    send_sms(phone, msg)
