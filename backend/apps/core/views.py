from django.utils import timezone
from rest_framework import status, serializers as drf_serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'], summary='Health check',
        description='Returns a lightweight status response for uptime checks.',
        responses={200: inline_serializer('HealthCheckResponse', fields={
            'status': drf_serializers.CharField(),
            'service': drf_serializers.CharField(),
            'timestamp': drf_serializers.DateTimeField(),
        })},
        examples=[OpenApiExample('Healthy', value={'status': 'ok', 'service': 'backend', 'timestamp': '2026-04-15T00:00:00Z'}, response_only=True)],
    )
    def get(self, request):
        return Response({'status': 'ok', 'service': 'backend', 'timestamp': timezone.now().isoformat()})


class NewsletterSubscribeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['System'], summary='Subscribe to newsletter',
        request=inline_serializer('NewsletterSub', fields={'email': drf_serializers.EmailField()}),
        responses={201: inline_serializer('NewsletterOK', fields={'detail': drf_serializers.CharField()})},
    )
    def post(self, request):
        from apps.core.models import NewsletterSubscriber
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        _, created = NewsletterSubscriber.objects.get_or_create(email=email)
        return Response(
            {'detail': 'Subscribed successfully.' if created else 'Already subscribed.'},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cart'],
        summary='Add tickets to cart',
        request=inline_serializer('CartAddRequest', fields={
            'event_id': drf_serializers.IntegerField(),
            'quantity': drf_serializers.IntegerField(min_value=1),
        }),
        responses={200: inline_serializer('CartAddResponse', fields={
            'success': drf_serializers.BooleanField(),
            'message': drf_serializers.CharField(),
            'event_title': drf_serializers.CharField(),
            'quantity': drf_serializers.IntegerField(),
        })},
    )
    def post(self, request):
        from apps.events.models import Event

        event_id = request.data.get('event_id')
        quantity = request.data.get('quantity', 1)

        if not event_id:
            return Response(
                {'detail': 'event_id is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError()
        except (TypeError, ValueError):
            return Response(
                {'detail': 'quantity must be a positive integer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response(
                {'detail': 'Event not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if event.status != Event.Status.APPROVED:
            return Response(
                {'detail': 'Event is not approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.start_date <= timezone.now():
            return Response(
                {'detail': 'Event has already started.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if event.tickets_available is None or event.tickets_available < quantity:
            return Response(
                {'detail': f'Not enough tickets available. Only {event.tickets_available or 0} tickets left.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'success': True,
            'message': f'{quantity} ticket(s) added to cart for "{event.title}"',
            'event_title': event.title,
            'quantity': quantity,
        })
