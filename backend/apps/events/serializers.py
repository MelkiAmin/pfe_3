from rest_framework import serializers
from .models import Event, Category, Favorite, EventReview
from apps.accounts.serializers import UserProfileSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']

class EventListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    organizer_name = serializers.CharField(source='organizer.full_name', read_only=True)
    tickets_sold = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    reviews_count = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'cover_image', 'event_type', 'status',
            'category', 'organizer_name', 'start_date', 'end_date',
            'city', 'country', 'is_free', 'tickets_sold', 'is_sold_out',
            'average_rating', 'reviews_count',
        ]

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
    class Meta:
        model = Event
        exclude = ['organizer', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        from django.utils.text import slugify
        import uuid
        title = validated_data.get('title', '')
        validated_data['slug'] = slugify(title) + '-' + str(uuid.uuid4())[:8]
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)

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
