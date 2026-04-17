from rest_framework import serializers
from .models import OrganizerProfile

class OrganizerProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = OrganizerProfile
        fields = ['id', 'user_name', 'user_email', 'organization_name', 'bio',
                  'logo', 'website', 'social_links', 'is_verified', 'total_events', 'created_at']
        read_only_fields = ['is_verified', 'total_events']