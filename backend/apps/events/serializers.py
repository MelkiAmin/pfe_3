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
    is_expired = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'cover_image', 'event_type', 'status',
            'category', 'organizer_name', 'start_date', 'end_date',
            'city', 'country', 'is_free', 'min_price', 'tickets_sold', 'is_sold_out',
            'is_expired', 'tickets_total', 'tickets_available',
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
    ticket_types = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_ticket_types(self, obj):
        from apps.tickets.serializers import TicketTypeSerializer
        return TicketTypeSerializer(obj.ticket_types.all(), many=True).data

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    ticket_price = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False, allow_null=True, default=0)
    ticket_quantity = serializers.IntegerField(min_value=1, write_only=True, required=False, allow_null=True, default=100)
    tickets_available = serializers.IntegerField(min_value=1, write_only=True, required=False, allow_null=True, default=100)
    category = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    start_date = serializers.DateTimeField(required=False, allow_null=True)
    end_date = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'category', 'cover_image',
            'event_type', 'venue_name', 'address', 'city', 'country', 'online_url',
            'start_date', 'end_date', 'max_capacity', 'is_free', 'tags',
            'ticket_price', 'ticket_quantity', 'tickets_available',
        ]
        extra_kwargs = {
            'category': {'required': False, 'allow_null': True, 'allow_blank': True},
            'cover_image': {'required': False, 'allow_null': True},
            'event_type': {'required': False, 'allow_blank': True},
            'venue_name': {'required': False, 'allow_blank': True},
            'address': {'required': False, 'allow_blank': True},
            'city': {'required': False, 'allow_blank': True},
            'country': {'required': False, 'allow_blank': True},
            'online_url': {'required': False, 'allow_blank': True},
            'max_capacity': {'required': False, 'allow_null': True},
            'is_free': {'required': False},
            'tags': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        import logging
        from django.utils.dateparse import parse_datetime
        logger = logging.getLogger(__name__)
        
        if self.instance is None:
            if not attrs.get('title'):
                raise serializers.ValidationError({'title': 'Le titre est requis'})
            if not attrs.get('description'):
                raise serializers.ValidationError({'description': 'La description est requise'})
            
            if not attrs.get('start_date'):
                raise serializers.ValidationError({'start_date': 'La date de début est requise'})
            if not attrs.get('end_date'):
                attrs['end_date'] = attrs.get('start_date')
            
            tickets_available = attrs.get('tickets_available', 0)
            if not tickets_available or tickets_available < 1:
                raise serializers.ValidationError({'tickets_available': 'Le nombre de billets disponibles doit être au moins 1'})
            
            attrs['status'] = Event.Status.PENDING

        logger.info(f"Validated attrs: {attrs.keys()}")
        logger.info(f"  start_date: {attrs.get('start_date')}")
        logger.info(f"  end_date: {attrs.get('end_date')}")
        logger.info(f"  tickets_available: {attrs.get('tickets_available')}")
        return super().validate(attrs)

    def create(self, validated_data):
        import logging
        from django.utils.text import slugify
        import uuid
        from apps.tickets.models import TicketType
        from .models import Category

        logger = logging.getLogger(__name__)
        
        ticket_price = validated_data.pop('ticket_price') or 0
        ticket_quantity = validated_data.pop('ticket_quantity') or 100
        tickets_available = validated_data.pop('tickets_available') or ticket_quantity
        title = validated_data.get('title') or ''
        
        category_value = validated_data.pop('category', None)
        category_obj = None
        if category_value:
            if isinstance(category_value, int):
                category_obj = Category.objects.filter(id=category_value).first()
            elif isinstance(category_value, str):
                category_obj = Category.objects.filter(slug=category_value).first()
                if not category_obj:
                    category_obj = Category.objects.filter(name__iexact=category_value).first()
        
        slug = slugify(title) + '-' + str(uuid.uuid4())[:8]
        organizer = self.context['request'].user
        status = Event.Status.PENDING
        
        logger.info(f"SERIALIZER CREATE: title={title}, category={category_value}, organizer={organizer.email}")

        event = Event.objects.create(
            title=title,
            description=validated_data.get('description') or '',
            category=category_obj,
            cover_image=validated_data.get('cover_image'),
            event_type=validated_data.get('event_type') or Event.EventType.IN_PERSON,
            venue_name=validated_data.get('venue_name') or '',
            address=validated_data.get('address') or '',
            city=validated_data.get('city') or '',
            country=validated_data.get('country') or '',
            online_url=validated_data.get('online_url') or '',
            start_date=validated_data.get('start_date'),
            end_date=validated_data.get('end_date'),
            max_capacity=validated_data.get('max_capacity'),
            tickets_total=ticket_quantity or 100,
            tickets_available=tickets_available,
            is_free=validated_data.get('is_free', False),
            tags=validated_data.get('tags') or [],
            slug=slug,
            organizer=organizer,
            status=status,
        )
        
        logger.info(f"EVENT CREATED: id={event.id}, status={event.status}, tickets_available={event.tickets_available}")

        TicketType.objects.create(
            event=event,
            name='Standard',
            price=ticket_price or 0,
            quantity=ticket_quantity or 100,
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


class ChatbotMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500, required=True)


class ChatbotResponseSerializer(serializers.Serializer):
    reply = serializers.CharField(required=False, allow_blank=True)
    response = serializers.CharField(required=False, allow_blank=True)
    events = EventListSerializer(many=True)
    detected_category = serializers.CharField(required=False, allow_null=True)
    intent = serializers.CharField(required=False, allow_blank=True)
    filters = serializers.DictField(required=False)


class EventStatusSummarySerializer(serializers.Serializer):
    pending_count = serializers.IntegerField()
    approved_count = serializers.IntegerField()
    rejected_count = serializers.IntegerField()
