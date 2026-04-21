from rest_framework import serializers

from apps.accounts.models import User
from apps.organizer.models import OrganizerProfile


class AdminUserListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    account_status = serializers.SerializerMethodField()
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
            'status',
            'phone',
            'is_active',
            'is_banned',
            'account_status',
            'ban_reason',
            'banned_at',
            'is_2fa_enabled',
            'created_at',
            'updated_at',
        ]

    def get_account_status(self, obj):
        if not obj.is_active:
            return 'banned'
        return 'active'


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[], required=False)
    account_status = serializers.ChoiceField(choices=['active', 'banned'], required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'role', 'account_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = User.Role.choices

    def validate_role(self, value):
        if value is None:
            return value
        request = self.context.get('request')
        if request and self.instance and request.user.pk == self.instance.pk and value != User.Role.ADMIN:
            raise serializers.ValidationError('You cannot remove your own admin role.')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        account_status = attrs.get('account_status')
        if request and self.instance and request.user.pk == self.instance.pk and account_status == 'banned':
            raise serializers.ValidationError({'account_status': 'You cannot ban your own account.'})
        return attrs

    def update(self, instance, validated_data):
        account_status = validated_data.pop('account_status', None)
        role = validated_data.pop('role', None)
        phone = validated_data.get('phone')

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = phone if phone is not None else instance.phone

        if role is not None:
            instance.role = role
            instance.is_staff = role == User.Role.ADMIN
            if role != User.Role.ADMIN:
                instance.is_superuser = False

        if account_status is not None:
            if account_status == 'banned':
                instance.is_active = False
                if not instance.banned_at:
                    from django.utils import timezone
                    instance.banned_at = timezone.now()
                    instance.ban_reason = 'Banned by admin'
            elif account_status == 'active':
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
