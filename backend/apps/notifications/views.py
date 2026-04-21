from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer

from .models import Notification
from .serializers import NotificationSerializer

mark_all_read_response = inline_serializer(
    name='MarkAllNotificationsReadResponse',
    fields={
        'detail': serializers.CharField(),
    },
)

unread_count_response = inline_serializer(
    name='UnreadNotificationCountResponse',
    fields={
        'unread_count': serializers.IntegerField(),
    },
)

@extend_schema_view(
    list=extend_schema(tags=['Notifications'], summary='List notifications'),
    retrieve=extend_schema(
        tags=['Notifications'],
        summary='Retrieve a notification',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
    destroy=extend_schema(
        tags=['Notifications'],
        summary='Delete a notification',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
)
class NotificationViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
        return Notification.objects.filter(recipient=self.request.user)

    @extend_schema(
        tags=['Notifications'],
        summary='Mark all notifications as read',
        responses={200: mark_all_read_response},
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'detail': 'All notifications marked as read.'})

    @extend_schema(
        tags=['Notifications'],
        summary='Mark one notification as read',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
        responses={200: NotificationSerializer},
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(NotificationSerializer(notification).data)

    @extend_schema(
        tags=['Notifications'],
        summary='Get unread notification count',
        responses={200: unread_count_response},
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
