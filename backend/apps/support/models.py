import uuid
from django.db import models
from django.conf import settings

class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN      = 'open',      'Open'
        IN_REVIEW = 'in_review', 'In Review'
        RESOLVED  = 'resolved',  'Resolved'
        CLOSED    = 'closed',    'Closed'

    class Priority(models.TextChoices):
        LOW    = 'low',    'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH   = 'high',   'High'
        URGENT = 'urgent', 'Urgent'

    ticket_ref  = models.CharField(max_length=12, unique=True, editable=False)
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject     = models.CharField(max_length=255)
    description = models.TextField()
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    priority    = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'support_tickets'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.ticket_ref:
            self.ticket_ref = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.ticket_ref} — {self.subject}'

class SupportMessage(models.Model):
    ticket    = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message   = models.TextField()
    is_staff  = models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']
