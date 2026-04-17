from django.db import models
from django.conf import settings

class KYCDocument(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',  'Pending'
        APPROVED  = 'approved', 'Approved'
        REJECTED  = 'rejected', 'Rejected'

    class DocType(models.TextChoices):
        PASSPORT    = 'passport',     'Passport'
        NATIONAL_ID = 'national_id',  'National ID'
        DRIVER_LIC  = 'driver_license','Driver License'

    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kyc')
    doc_type   = models.CharField(max_length=30, choices=DocType.choices)
    front_image= models.ImageField(upload_to='kyc/docs/', null=True, blank=True)
    back_image = models.ImageField(upload_to='kyc/docs/', null=True, blank=True)
    selfie     = models.ImageField(upload_to='kyc/selfies/', null=True, blank=True)
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'kyc_documents'

    def __str__(self):
        return f'KYC for {self.user.email} — {self.status}'
