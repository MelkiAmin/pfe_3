from rest_framework import serializers
from .models import KYCDocument

class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['id','doc_type','front_image','back_image','selfie',
                  'status','rejection_reason','submitted_at','reviewed_at']
        read_only_fields = ['id','status','rejection_reason','submitted_at','reviewed_at']
