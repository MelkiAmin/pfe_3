from django.db import models
from django.conf import settings

class OrganizerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organizer_profile'
    )
    organization_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    logo = models.ImageField(upload_to='organizers/logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    total_events = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizer_profiles'

    def __str__(self):
        return self.organization_name