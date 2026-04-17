from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Type(models.TextChoices):
        TICKET_PURCHASED = 'ticket_purchased', 'Ticket Purchased'
        EVENT_REMINDER = 'event_reminder', 'Event Reminder'
        EVENT_CANCELLED = 'event_cancelled', 'Event Cancelled'
        EVENT_UPDATED = 'event_updated', 'Event Updated'
        PAYMENT_CONFIRMED = 'payment_confirmed', 'Payment Confirmed'
        PAYMENT_FAILED = 'payment_failed', 'Payment Failed'
        GENERAL = 'general', 'General'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.GENERAL)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.notification_type} for {self.recipient.email}'