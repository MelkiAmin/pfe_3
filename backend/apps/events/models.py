from django.db import models
from django.conf import settings
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'event_categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class EventType(models.TextChoices):
        IN_PERSON = 'in_person', 'In Person'
        ONLINE = 'online', 'Online'
        HYBRID = 'hybrid', 'Hybrid'

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organized_events'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='events')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='events/covers/', null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.IN_PERSON)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    venue_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    online_url = models.URLField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_capacity = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def tickets_sold(self) -> int:
        return self.tickets.filter(status='confirmed').count()

    @property
    def is_sold_out(self) -> bool:
        if self.max_capacity is None:
            return False
        return self.tickets_sold >= self.max_capacity

    @property
    def reviews_count(self) -> int:
        return self.reviews.count()

    @property
    def average_rating(self) -> float:
        data = self.reviews.aggregate(avg=Avg('rating'))
        avg = data.get('avg')
        return float(avg) if avg is not None else 0.0

class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_events',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_favorites'
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} -> {self.event.title}'

class EventReview(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_reviews',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_reviews'
        unique_together = ('user', 'event')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event.title} review by {self.user.email}'
