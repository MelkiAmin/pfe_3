import pytest
from rest_framework import status
from apps.accounts.models import User
from apps.kyc.models import KYCDocument

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='kyc@test.com', password='KycPass123!',
        first_name='K', last_name='User', role=User.Role.ATTENDEE
    )

@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email='admin@test.com', password='AdminPass123!',
        first_name='Admin', last_name='User', role=User.Role.ADMIN, is_staff=True
    )

class TestKYC:
    def test_get_kyc_status_unauthenticated(self, api_client):
        resp = api_client.get('/api/kyc/status/')
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_kyc_status_creates_default(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.get('/api/kyc/status/')
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data['status'] == 'pending'

    def test_admin_can_list_kyc(self, api_client, admin):
        api_client.force_authenticate(user=admin)
        resp = api_client.get('/api/kyc/admin/')
        assert resp.status_code == status.HTTP_200_OK

    def test_admin_can_approve_kyc(self, api_client, admin, user):
        kyc = KYCDocument.objects.create(user=user, doc_type='national_id')
        api_client.force_authenticate(user=admin)
        resp = api_client.post(f'/api/kyc/admin/{kyc.id}/action/', {'action': 'approve'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        kyc.refresh_from_db()
        assert kyc.status == KYCDocument.Status.APPROVED

    def test_admin_can_reject_with_reason(self, api_client, admin, user):
        kyc = KYCDocument.objects.create(user=user, doc_type='passport')
        api_client.force_authenticate(user=admin)
        resp = api_client.post(f'/api/kyc/admin/{kyc.id}/action/', {
            'action': 'reject', 'rejection_reason': 'Image is blurry'
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        kyc.refresh_from_db()
        assert kyc.status == KYCDocument.Status.REJECTED
        assert kyc.rejection_reason == 'Image is blurry'
