import pytest
from rest_framework import status
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.notifications.tasks import create_notification

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='notif@test.com', password='Pass123!',
        first_name='N', last_name='User', role=User.Role.ATTENDEE
    )

class TestNotifications:
    def test_list_notifications_empty(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.get('/api/notifications/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['count'] == 0

    def test_mark_all_read(self, api_client, user):
        create_notification(user, Notification.Type.GENERAL, 'Test', 'Message 1')
        create_notification(user, Notification.Type.GENERAL, 'Test', 'Message 2')
        api_client.force_authenticate(user=user)
        resp = api_client.post('/api/notifications/mark_all_read/')
        assert resp.status_code == status.HTTP_200_OK
        assert Notification.objects.filter(recipient=user, is_read=False).count() == 0

    def test_unread_count(self, api_client, user):
        create_notification(user, Notification.Type.GENERAL, 'T', 'M')
        api_client.force_authenticate(user=user)
        resp = api_client.get('/api/notifications/unread_count/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['unread_count'] == 1

    def test_mark_single_notification_read(self, api_client, user):
        notif = create_notification(user, Notification.Type.GENERAL, 'T', 'M')
        api_client.force_authenticate(user=user)
        resp = api_client.post(f'/api/notifications/{notif.id}/mark_read/')
        assert resp.status_code == status.HTTP_200_OK
        notif.refresh_from_db()
        assert notif.is_read is True
