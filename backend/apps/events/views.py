from rest_framework import viewsets, permissions, filters, mixins, status, serializers as drf_serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer, OpenApiResponse

from .models import Event, Category, Favorite, EventReview
from .serializers import (
    EventListSerializer, EventDetailSerializer,
    EventCreateUpdateSerializer, CategorySerializer,
    FavoriteSerializer, EventReviewSerializer,
    ChatbotMessageSerializer, ChatbotResponseSerializer,
    EventStatusSummarySerializer,
)
from .recommendation_engine import recommend_events, get_popular_events, get_user_preferred_categories
from .chatbot_service import chatbot_service
from utils.permissions import IsOrganizerOrAdmin, IsOrganizerUser, IsOwnerOrAdmin, IsAdminUser

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
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Events'], summary='DEBUG: Get ALL events in database',
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser], url_path='debug-all')
    def debug_all_events(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        all_events = Event.objects.all().select_related('organizer')
        logger.info(f"DEBUG: Total events in DB: {all_events.count()}")
        
        for e in all_events:
            logger.info(f"  Event: {e.id} | {e.title} | status={e.status} | organizer={e.organizer.email}")
        
        return Response({
            'total': all_events.count(),
            'events': [{
                'id': e.id,
                'title': e.title,
                'status': e.status,
                'organizer_email': e.organizer.email,
            } for e in all_events]
        })

    def perform_create(self, serializer):
        import logging
        from apps.notifications.tasks import create_notification
        from apps.notifications.models import Notification
        
        logger = logging.getLogger(__name__)
        
        user = self.request.user
        logger.info(f"VIEW perform_create: user={user.email}, role={user.role}")
        
        event = serializer.save()
        logger.info(f"VIEW perform_create: saved event id={event.id}, status={event.status}")
        
        create_notification(
            recipient=user,
            notification_type=Notification.Type.EVENT_SUBMITTED,
            title='Event submitted',
            message=f'Your event "{event.title}" has been submitted and is pending approval.',
            data={'event_id': event.id},
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def get_permissions(self):
        request = getattr(self, 'request', None)
        path = getattr(request, 'path', '') if request else ''

        if path == '/api/events/featured/' or path.startswith('/api/events/featured'):
            return [permissions.AllowAny()]
        if path == '/api/events/' and request and request.method == 'GET':
            return [permissions.AllowAny()]
        if path.startswith('/api/events/') and path != '/api/events/':
            pk = path.split('/api/events/')[-1].split('/')[0]
            if pk.isdigit() or pk:
                return [permissions.AllowAny()]

        action = getattr(self, 'action', None)
        if action in ['list', 'retrieve', 'featured']:
            return [permissions.AllowAny()]
        if action == 'create':
            return [IsOrganizerUser()]
        return [IsOwnerOrAdmin()]

    def get_queryset(self):
        import logging
        from django.utils import timezone
        logger = logging.getLogger(__name__)
        
        qs = super().get_queryset()

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        is_free = self.request.query_params.get('is_free')

        if date_from:
            qs = qs.filter(start_date__gte=date_from)
        if date_to:
            qs = qs.filter(end_date__lte=date_to)
        if is_free is not None:
            qs = qs.filter(is_free=is_free.lower() == 'true')

        if self.action == 'list':
            user = self.request.user
            user_email = getattr(user, 'email', 'anonymous') if user else 'anonymous'
            user_auth = user.is_authenticated if user else False
            user_role = str(user.role) if user and hasattr(user, 'role') else ''
            
            if user_auth and user_role == str(user.Role.ADMIN):
                return qs
            if user_auth and user_role == str(user.Role.ORGANIZER):
                return qs.filter(
                    Q(organizer=self.request.user) | 
                    Q(status=Event.Status.APPROVED, start_date__gt=timezone.now())
                ).distinct()

            return qs.filter(status=Event.Status.APPROVED, start_date__gt=timezone.now())

        if self.action == 'retrieve':
            user = self.request.user
            user_auth = user.is_authenticated if user else False
            user_role = str(user.role) if user and hasattr(user, 'role') else ''
            
            if user_auth and user_role == str(user.Role.ADMIN):
                return qs
            if user_auth and user_role == str(user.Role.ORGANIZER):
                return qs.filter(
                    Q(organizer=user) | 
                    Q(status__in=[Event.Status.APPROVED, Event.Status.COMPLETED], start_date__gt=timezone.now()),
                ).distinct()

            return qs.filter(status__in=[Event.Status.APPROVED, Event.Status.COMPLETED], start_date__gt=timezone.now())
        return qs

    @extend_schema(
        tags=['Events'],
        summary='List featured events',
        parameters=[
            OpenApiParameter('limit', int, OpenApiParameter.QUERY, description='Number of featured events to return (default 6)'),
        ],
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='featured')
    def featured_events(self, request):
        from django.utils import timezone
        from django.core.cache import cache
        
        cache_key = 'events:featured'
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)
        
        try:
            limit_param = request.query_params.get('limit', '6')
            limit = int(limit_param) if limit_param else 6
        except (ValueError, TypeError):
            limit = 6

        if limit < 1:
            limit = 6
        if limit > 20:
            limit = 20

        events = Event.objects.filter(
            status=Event.Status.APPROVED,
            start_date__gt=timezone.now()
        ).select_related('organizer', 'category').order_by('-created_at')[:limit]
        serializer = EventListSerializer(events, many=True, context={'request': request})
        data = serializer.data
        cache.set(cache_key, data, timeout=300)
        return Response(data)

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
        tags=['Events'], summary='Get organizer event status summary',
    )
    @action(detail=False, methods=['get'], permission_classes=[IsOrganizerOrAdmin], url_path='status-summary')
    def status_summary(self, request):
        import logging
        logger = logging.getLogger(__name__)
        user = request.user
        
        logger.info(f"status_summary called by user: {user.email}, role: {user.role}")
        
        if str(user.role) == str(user.Role.ADMIN):
            logger.info("Admin mode - returning all events")
            pending_count = Event.objects.filter(status=Event.Status.PENDING).count()
            approved_count = Event.objects.filter(status=Event.Status.APPROVED).count()
            rejected_count = Event.objects.filter(status=Event.Status.REJECTED).count()
        else:
            logger.info(f"Organizer mode - filtering by organizer: {user.id}")
            pending_count = Event.objects.filter(organizer=user, status=Event.Status.PENDING).count()
            approved_count = Event.objects.filter(organizer=user, status=Event.Status.APPROVED).count()
            rejected_count = Event.objects.filter(organizer=user, status=Event.Status.REJECTED).count()
            
        logger.info(f"Status counts - pending: {pending_count}, approved: {approved_count}, rejected: {rejected_count}")
        
        return Response({
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
        })

    @extend_schema(
        tags=['Events'], summary='Get pending events for admin',
        responses={200: EventListSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsOrganizerOrAdmin], url_path='pending')
    def pending_events(self, request):
        if request.user.role == 'admin':
            qs = Event.objects.filter(status=Event.Status.PENDING).select_related('category', 'organizer')
        else:
            qs = Event.objects.filter(organizer=request.user, status=Event.Status.PENDING).select_related('category', 'organizer')
        
        serializer = EventListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        tags=['Events'], summary='Approve an event',
        responses={200: EventDetailSerializer()},
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='approve')
    def approve_event(self, request, pk=None):
        from apps.notifications.models import Notification
        from apps.notifications.tasks import create_notification, send_sendgrid_email
        
        event = self.get_object()
        event.status = Event.Status.APPROVED
        event.save(update_fields=['status', 'updated_at'])
        
        create_notification(
            recipient=event.organizer,
            notification_type=Notification.Type.EVENT_APPROVED,
            title=f'Event approved: {event.title}',
            message=f'Your event "{event.title}" has been approved and is now live!',
            data={'event_id': event.id},
        )
        
        try:
            send_sendgrid_email(
                to_email=event.organizer.email,
                subject=f'Event approved: {event.title}',
                text_content=f'Your event "{event.title}" has been approved and is now live on Planova!',
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send approval email: {e}")
        
        return Response(EventDetailSerializer(event, context={'request': request}).data)

    @extend_schema(
        tags=['Events'], summary='Reject an event',
        request=inline_serializer('RejectEvent', fields={
            'reason': drf_serializers.CharField(required=False, allow_blank=True),
        }),
        responses={200: EventDetailSerializer()},
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='reject')
    def reject_event(self, request, pk=None):
        from apps.notifications.models import Notification
        from apps.notifications.tasks import create_notification, send_sendgrid_email
        
        event = self.get_object()
        reason = request.data.get('reason', '')
        event.status = Event.Status.REJECTED
        event.save(update_fields=['status', 'updated_at'])
        
        create_notification(
            recipient=event.organizer,
            notification_type=Notification.Type.EVENT_REJECTED,
            title=f'Event rejected: {event.title}',
            message=f'Your event "{event.title}" was not approved. Reason: {reason or "Please contact support for details."}',
            data={'event_id': event.id},
        )
        
        try:
            send_sendgrid_email(
                to_email=event.organizer.email,
                subject=f'Event rejected: {event.title}',
                text_content=f'Your event "{event.title}" was not approved. Reason: {reason or "Please contact support for details."}',
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to send rejection email: {e}")
        
        return Response(EventDetailSerializer(event, context={'request': request}).data)

    @extend_schema(
        tags=['Events'], summary='Get my organized events',
        responses={200: EventListSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], permission_classes=[IsOrganizerOrAdmin], url_path='my-events')
    def my_events(self, request):
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"my_events called by user: {request.user.email}, role: {request.user.role}")
        
        qs = Event.objects.filter(organizer=request.user).select_related('category')
        logger.info(f"Total events for organizer: {qs.count()}")
        
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


# ── Recommendations ────────────────────────────────────────────────────────
@extend_schema(
    tags=['Recommendations'],
    summary='Get personalized event recommendations',
    parameters=[
        OpenApiParameter('limit', int, OpenApiParameter.QUERY, description='Number of events to return (default 10)'),
    ],
)
@action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
def recommendations(self, request):
    from django.utils import timezone
    from django.db.models import Count, Q
    
    try:
        limit = int(request.query_params.get('limit', 10))
        limit = max(1, min(limit, 20))
    except (ValueError, TypeError):
        limit = 10
    
    recommended = recommend_events(request.user, limit=limit)
    serializer = EventListSerializer(recommended, many=True, context={'request': request})
    return Response({
        'recommendations': serializer.data,
        'count': len(recommended),
    })


@extend_schema(
    tags=['Recommendations'],
    summary='Get popular events',
    parameters=[
        OpenApiParameter('limit', int, OpenApiParameter.QUERY, description='Number of events to return (default 10)'),
    ],
)
@action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='popular')
def popular_events(self, request):
    try:
        limit = int(request.query_params.get('limit', 10))
        limit = max(1, min(limit, 20))
    except (ValueError, TypeError):
        limit = 10
    
    events = get_popular_events(limit)
    serializer = EventListSerializer(events, many=True, context={'request': request})
    return Response({
        'popular': serializer.data,
        'count': len(events),
    })


@extend_schema(
    tags=['Recommendations'],
    summary='Get similar events',
    parameters=[
        OpenApiParameter('limit', int, OpenApiParameter.QUERY, description='Number of events to return (default 5)'),
    ],
)
@action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny], url_path='similar')
def similar_events(self, request, pk=None):
    from .recommendation_engine import get_similar_events
    
    try:
        limit = int(request.query_params.get('limit', 5))
        limit = max(1, min(limit, 10))
    except (ValueError, TypeError):
        limit = 5
    
    event = self.get_object()
    similar = get_similar_events(event, limit=limit)
    serializer = EventListSerializer(similar, many=True, context={'request': request})
    return Response({
        'similar': serializer.data,
        'count': len(similar),
    })


EventViewSet.recommendations = recommendations
EventViewSet.popular_events = popular_events
EventViewSet.similar_events = similar_events


# ── Chatbot AI ────────────────────────────────────────────────────────────
class ChatbotViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    CATEGORY_KEYWORDS = {
        'concert': ['concert', 'musique', 'musical', 'festival', 'guitar', 'piano', 'rock', 'jazz', ' RAP', 'chanson'],
        'sport': ['sport', 'football', 'basket', 'tennis', 'match', 'rugby', 'athletisme', 'competition'],
        'business': ['business', 'entreprise', 'professionnel', 'conference', 'formation', 'startup', 'networking'],
        'culturel': ['culture', 'art', 'theatre', 'musée', 'exposition', 'peinture', 'danse', 'spectacle'],
        'technologie': ['tech', 'technologie', 'informatique', 'coding', 'developer', 'IA', 'AI', 'digital'],
        'gastronomie': ['gastronomie', 'food', 'restaurant', 'cuisine', 'vin', 'degustation'],
        'education': ['education', 'formation', 'cours', 'workshop', 'séminaire', 'conference'],
    }
    
    def _detect_category(self, message: str) -> tuple[str | None, list[Category]]:
        from django.utils.text import slugify
        from django.utils import timezone
        
        message_lower = message.lower()
        
        for category_name, keywords in self.CATEGORY_KEYWORDS.items():
            if any(kw in message_lower for kw in keywords):
                categories = Category.objects.filter(
                    slug__icontains=category_name,
                    events__status=Event.Status.APPROVED,
                    events__start_date__gte=timezone.now()
                ).distinct()
                
                if categories.exists():
                    return category_name, list(categories[:3])
        
        categories = Category.objects.filter(
            events__status=Event.Status.APPROVED,
            events__start_date__gte=timezone.now()
        ).annotate(
            event_count=Count('events')
        ).order_by('-event_count')[:3]
        
        return None, list(categories)
    
    def _generate_reply(self, message: str, category: str | None, events_count: int) -> str:
        message_lower = message.lower()
        
        greetings = ['bonjour', 'salut', 'hello', 'hi', 'coucou']
        if any(g in message_lower for g in greetings):
            return "Bonjour ! Je suis votre assistant événementiel. Dites-moi quel type d'événement vous intéresse (concert, sport, business, culture...) et je vous recommande les meilleurs événements !"
        
        if any(word in message_lower for word in ['merci', 'thanks', 'appreciate']):
            return "Avec plaisir ! N'hésitez pas si vous avez d'autres questions sur nos événements."
        
        if events_count > 0:
            if category:
                category_display = category.capitalize()
                return f"Voici les événements {category_display} que je vous recommande :"
            else:
                return "Voici les événements que je vous recommande selon vos préférences :"
        else:
            return "Désolé, je n'ai pas trouvé d'événements correspondant à votre demande. Essayez avec d'autres mots-clés comme 'concert', 'sport', 'business' ou 'culture'."
    
    @extend_schema(
        tags=['Chatbot'],
        summary='Send message to intelligent chatbot',
        request=ChatbotMessageSerializer,
        responses={200: ChatbotResponseSerializer},
    )
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def chat(self, request):
        """
        Intelligent chatbot endpoint
        - Detects user intent (greeting, search, filter)
        - Extracts filters (category, city, date, price)
        - Queries database dynamically
        - Returns natural language response + events
        """
        print(f"[Chatbot] Request: {request.data}")

        # Validate input
        serializer = ChatbotMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'response': 'Message invalide. Veuillez réessayer.',
                'events': [],
                'intent': 'error',
            }, status=400)

        message = serializer.validated_data['message']

        # Process with intelligent service
        result = chatbot_service.process_message(message)

        # Serialize events
        event_serializer = EventListSerializer(
            result['events'],
            many=True,
            context={'request': request}
        )

        print(f"[Chatbot] Response: intent={result['intent']}, events_count={len(result['events'])}")

        return Response({
            'response': result['response'],
            'events': event_serializer.data,
            'intent': result['intent'],
            'filters': result['filters'],
        })
