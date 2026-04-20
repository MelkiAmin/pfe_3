from rest_framework import serializers
from .models import Event, Category, Favorite, EventReview
from apps.accounts.serializers import UserProfileSerializer
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.notifications.tasks import create_notification

class CategorySerializer(serializers.ModelSerializer):
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'events_count']

    def get_events_count(self, obj):
        from apps.events.models import Event
        return Event.objects.filter(category=obj, status=Event.Status.APPROVED).count()

class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    tickets_sold = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'cover_image', 'event_type', 'status',
            'category', 'organizer_name', 'start_date', 'end_date',
            'city', 'country', 'is_free', 'min_price', 'tickets_sold', 'is_sold_out',
            'average_rating', 'reviews_count',
        ]

    def get_min_price(self, obj):
        from apps.tickets.models import TicketType
        ticket_type = TicketType.objects.filter(event=obj).order_by('price').first()
        if ticket_type:
            return str(ticket_type.price)
        return None

class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    organizer = UserProfileSerializer(read_only=True)
    tickets_sold = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = '__all__'

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    ticket_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    ticket_quantity = serializers.IntegerField(min_value=1, write_only=True, required=False)

    class Meta:
        model = Event
        exclude = ['organizer', 'slug', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance is None:
            required_fields = {
                'cover_image': attrs.get('cover_image'),
                'title': attrs.get('title'),
                'description': attrs.get('description'),
                'ticket_price': attrs.get('ticket_price'),
                'ticket_quantity': attrs.get('ticket_quantity'),
            }
            missing = [field for field, value in required_fields.items() if value in [None, '', []]]
            if missing:
                raise serializers.ValidationError({
                    field: 'This field is required.' for field in missing
                })

            attrs['status'] = Event.Status.PENDING

        return super().validate(attrs)

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid
        from apps.tickets.models import TicketType

        ticket_price = validated_data.pop('ticket_price')
        ticket_quantity = validated_data.pop('ticket_quantity')
        title = validated_data.get('title', '')
        validated_data['slug'] = slugify(title) + '-' + str(uuid.uuid4())[:8]
        validated_data['organizer'] = self.context['request'].user
        validated_data['status'] = Event.Status.PENDING

        event = super().create(validated_data)
        TicketType.objects.create(
            event=event,
            name='Standard',
            price=ticket_price,
            quantity=ticket_quantity,
        )

        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            create_notification(
                recipient=admin,
                notification_type=Notification.Type.EVENT_SUBMITTED,
                title=f'New event pending validation: {event.title}',
                message=f'{event.organizer.full_name} submitted "{event.title}" for review.',
                data={'event_id': event.id, 'organizer_id': event.organizer_id},
            )

        return event

class FavoriteSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'event', 'event_title', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        favorite, _ = Favorite.objects.get_or_create(**validated_data)
        return favorite

class EventReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = EventReview
        fields = ['id', 'event', 'user', 'user_name', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        review, created = EventReview.objects.get_or_create(
            user=validated_data['user'],
            event=validated_data['event'],
            defaults={
                'rating': validated_data['rating'],
                'comment': validated_data.get('comment', ''),
            },
        )
        if not created:
            review.rating = validated_data['rating']
            review.comment = validated_data.get('comment', '')
            review.save()
        return review
