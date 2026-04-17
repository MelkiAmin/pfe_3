from django.utils import timezone
from rest_framework import status, serializers as drf_serializers
from rest_framework.permissions import AllowAny
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
