from rest_framework import serializers

from apps.accounts.models import User
from apps.organizer.models import OrganizerProfile


class AdminUserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    status = serializers.SerializerMethodField()
    is_banned = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'phone',
            'is_active',
            'is_banned',
            'status',
            'ban_reason',
            'banned_at',
            'is_email_verified',
            'is_2fa_enabled',
            'created_at',
            'updated_at',
        ]

    def get_status(self, obj):
        return 'banned' if obj.is_banned else 'active'


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=['active', 'banned'], required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'status']

    def validate_role(self, value):
        request = self.context.get('request')
        if request and request.user.pk == self.instance.pk and value != User.Role.ADMIN:
            raise serializers.ValidationError('You cannot remove your own admin role.')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        status_value = attrs.get('status')
        if request and request.user.pk == self.instance.pk and status_value == 'banned':
            raise serializers.ValidationError({'status': 'You cannot ban your own account.'})
        return attrs

    def update(self, instance, validated_data):
        status_value = validated_data.pop('status', None)
        role = validated_data.get('role')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if role is not None:
            instance.is_staff = role == User.Role.ADMIN
            if role != User.Role.ADMIN:
                instance.is_superuser = False

        if status_value == 'banned':
            instance.is_active = False
            if not instance.banned_at:
                from django.utils import timezone
                instance.banned_at = timezone.now()
        elif status_value == 'active':
            instance.is_active = True
            instance.banned_at = None
            instance.ban_reason = ''

        instance.save()
        return instance


class AdminUserBanSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default='')


class AdminOrganizerSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    created_at = serializers.DateTimeField(source='user.created_at', read_only=True)

    class Meta:
        model = OrganizerProfile
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_role', 'is_active',
            'organization_name', 'bio', 'logo', 'website', 'social_links',
            'is_verified', 'total_events', 'created_at',
        ]


class AdminOrganizerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizerProfile
        fields = ['organization_name', 'bio', 'logo', 'website', 'social_links', 'is_verified']


class AdminOrganizerStatsSerializer(serializers.Serializer):
    total_events = serializers.IntegerField()
    published_events = serializers.IntegerField()
    total_tickets_sold = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
