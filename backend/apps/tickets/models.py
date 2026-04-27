import uuid
from django.db import models
from django.conf import settings
from utils.helpers import generate_qr_code

class TicketType(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='ticket_types')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    quantity_sold = models.PositiveIntegerField(default=0)
    sale_start = models.DateTimeField(null=True, blank=True)
    sale_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ticket_types'

    def __str__(self):
        return f'{self.event.title} - {self.name}'

    @property
    def available_quantity(self) -> int:
        return self.quantity - self.quantity_sold

    @property
    def is_available(self) -> bool:
        return self.available_quantity > 0

class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        USED = 'used', 'Used'
        REFUNDED = 'refunded', 'Refunded'

    ticket_number = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT, related_name='tickets')
    event = models.ForeignKey('events.Event', on_delete=models.PROTECT, related_name='tickets')
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code = models.ImageField(upload_to='tickets/qr/', null=True, blank=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ticket #{self.ticket_number} - {self.event.title}'

    def build_qr_payload(self) -> str:
        return (
            f'ticket_number={self.ticket_number};'
            f'ticket_id={self.pk};'
            f'event_id={self.event_id};'
            f'attendee_id={self.attendee_id};'
            f'status={self.status}'
        )

    def attach_qr_code(self, save=True):
        if self.qr_code:
            return self.qr_code

        qr_file = generate_qr_code(self.build_qr_payload())
        self.qr_code.save(f'ticket_{self.ticket_number}.png', qr_file, save=False)

        if save:
            self.save(update_fields=['qr_code', 'updated_at'])

        return self.qr_code

    def get_qr_code_url(self) -> str | None:
        if not self.qr_code:
            return None
        from django.conf import settings
        from urllib.parse import urljoin
        media_url = getattr(settings, 'MEDIA_URL', '/media/')
        return urljoin(media_url, self.qr_code.name)
