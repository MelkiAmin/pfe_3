from rest_framework import viewsets, permissions, filters, mixins, status, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer, OpenApiResponse

from .models import Event, Category, Favorite, EventReview
from .serializers import (
    EventListSerializer, EventDetailSerializer,
    EventCreateUpdateSerializer, CategorySerializer,
    FavoriteSerializer, EventReviewSerializer,
)
from utils.permissions import IsOrganizerOrAdmin, IsOrganizerUser, IsOwnerOrAdmin

# ── Category ────────────────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List categories'),
    retrieve=extend_schema(tags=['Events'], summary='Retrieve a category'),
    create=extend_schema(tags=['Events'], summary='Create a category'),
    update=extend_schema(tags=['Events'], summary='Replace a category'),
    partial_update=extend_schema(tags=['Events'], summary='Update a category'),
    destroy=extend_schema(tags=['Events'], summary='Delete a category'),
)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsOrganizerOrAdmin()]


# ── Event ────────────────────────────────────────────────────────────────
event_status_action_serializer = inline_serializer(
    name='EventStatusAction',
    fields={
        'action': drf_serializers.ChoiceField(choices=['cancel', 'complete']),
        'reason': drf_serializers.CharField(required=False, allow_blank=True),
    },
)

@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List events'),
    retrieve=extend_schema(tags=['Events'], summary='Retrieve an event'),
    create=extend_schema(tags=['Events'], summary='Create an event'),
    update=extend_schema(tags=['Events'], summary='Replace an event'),
    partial_update=extend_schema(tags=['Events'], summary='Update an event'),
    destroy=extend_schema(tags=['Events'], summary='Delete an event'),
)
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('organizer', 'category').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'event_type', 'category', 'city', 'is_free']
    search_fields = ['title', 'description', 'city', 'venue_name']
    ordering_fields = ['start_date', 'created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [IsOrganizerUser()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            if self.request.user.is_authenticated and self.request.user.role == 'admin':
                return qs
            if self.request.user.is_authenticated and self.request.user.role == 'organizer':
                return qs.filter(Q(organizer=self.request.user) | Q(status=Event.Status.APPROVED)).distinct()

            qs = qs.filter(status=Event.Status.APPROVED)

        if self.action == 'retrieve':
            user = self.request.user
            if user.is_authenticated and user.role == 'admin':
                return qs
            if user.is_authenticated and user.role == 'organizer':
                return qs.filter(
                    Q(organizer=user) | Q(status__in=[Event.Status.APPROVED, Event.Status.COMPLETED]),
                ).distinct()

            return qs.filter(status__in=[Event.Status.APPROVED, Event.Status.COMPLETED])
        return qs

    @extend_schema(
        tags=['Events'], summary='Change event status (cancel / complete)',
        request=event_status_action_serializer,
        responses={
            200: EventDetailSerializer(),
            400: OpenApiResponse(description='Invalid action or state'),
            403: OpenApiResponse(description='Not allowed'),
        },
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin], url_path='status')
    def change_status(self, request, pk=None):
        event = self.get_object()
        act = request.data.get('action')

        transitions = {
            'cancel':   ([Event.Status.PENDING, Event.Status.APPROVED], Event.Status.CANCELLED),
            'complete': ([Event.Status.APPROVED], Event.Status.COMPLETED),
        }

        if act not in transitions:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_from, to_status = transitions[act]
        if allowed_from and event.status not in allowed_from:
            return Response(
                {'detail': f'Event cannot transition from "{event.status}" via "{act}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if act == 'cancel' and event.status == Event.Status.CANCELLED:
            return Response({'detail': 'Event is already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        event.status = to_status
        event.save(update_fields=['status', 'updated_at'])

        # Notify attendees on cancellation
        if act == 'cancel':
            from apps.tickets.models import Ticket
            from apps.notifications.tasks import send_event_cancellation_email, create_notification
            from apps.notifications.models import Notification
            tickets = Ticket.objects.filter(
                event=event, status=Ticket.Status.CONFIRMED
            ).select_related('attendee')
            for ticket in tickets:
                send_event_cancellation_email.delay(ticket.attendee.email, event.title)
                create_notification(
                    recipient=ticket.attendee,
                    notification_type=Notification.Type.EVENT_CANCELLED,
                    title=f'Event cancelled: {event.title}',
                    message=f'The event "{event.title}" has been cancelled. A refund will be processed if applicable.',
                    data={'event_id': event.id},
                )

        return Response(EventDetailSerializer(event, context={'request': request}).data)

    @extend_schema(
        tags=['Events'], summary='Get my organized events',
        responses={200: EventListSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsOrganizerOrAdmin], url_path='my-events')
    def my_events(self, request):
        qs = Event.objects.filter(organizer=request.user).select_related('category')
        page = self.paginate_queryset(qs)
        serializer = EventListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


# ── Favorites ───────────────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List favorites'),
    create=extend_schema(tags=['Events'], summary='Add a favorite'),
    destroy=extend_schema(tags=['Events'], summary='Remove a favorite',
                          parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)]),
)
class FavoriteViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('event')


# ── Reviews ─────────────────────────────────────────────────────────────
@extend_schema_view(
    list=extend_schema(tags=['Events'], summary='List event reviews'),
    retrieve=extend_schema(tags=['Events'], summary='Retrieve an event review'),
    create=extend_schema(tags=['Events'], summary='Create an event review'),
    update=extend_schema(tags=['Events'], summary='Replace a review'),
    partial_update=extend_schema(tags=['Events'], summary='Update a review'),
    destroy=extend_schema(tags=['Events'], summary='Delete a review'),
)
class EventReviewViewSet(viewsets.ModelViewSet):
    serializer_class = EventReviewSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return EventReview.objects.select_related('user', 'event').all()
