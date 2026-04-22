from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.events.models import Event
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.notifications.tasks import create_notification


@receiver(post_save, sender=Event)
def event_status_changed(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(role=User.Role.ADMIN, is_active=True)
        for admin in admins:
            create_notification(
                recipient=admin,
                notification_type=Notification.Type.EVENT_SUBMITTED,
                title='Nouvel événement en attente de validation',
                message=f'Un nouvel événement "{instance.title}" a été soumis et attend votre validation.',
                data={'event_id': instance.id, 'event_status': instance.status},
            )