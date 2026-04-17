from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers

from .models import Ticket, TicketType
from .serializers import TicketSerializer, TicketTypeSerializer
from utils.permissions import IsOrganizerOrAdmin

ticket_check_in_response = inline_serializer(
    name='TicketCheckInResponse',
    fields={
        'detail': serializers.CharField(),
        'ticket': TicketSerializer(),
    },
)

@extend_schema_view(
    list=extend_schema(tags=['Tickets'], summary='List ticket types'),
    retrieve=extend_schema(tags=['Tickets'], summary='Retrieve a ticket type'),
    create=extend_schema(tags=['Tickets'], summary='Create a ticket type'),
    update=extend_schema(tags=['Tickets'], summary='Replace a ticket type'),
    partial_update=extend_schema(tags=['Tickets'], summary='Update a ticket type'),
    destroy=extend_schema(tags=['Tickets'], summary='Delete a ticket type'),
)
class TicketTypeViewSet(viewsets.ModelViewSet):
    queryset = TicketType.objects.select_related('event').all()
    serializer_class = TicketTypeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsOrganizerOrAdmin()]

@extend_schema_view(
    list=extend_schema(tags=['Tickets'], summary='List tickets'),
    retrieve=extend_schema(
        tags=['Tickets'],
        summary='Retrieve a ticket',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
    create=extend_schema(tags=['Tickets'], summary='Create a ticket'),
    destroy=extend_schema(
        tags=['Tickets'],
        summary='Delete a ticket',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
)
class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['organizer', 'admin']:
            return Ticket.objects.select_related('ticket_type', 'event', 'attendee').all()
        return Ticket.objects.filter(attendee=user).select_related('ticket_type', 'event')

    @extend_schema(
        tags=['Tickets'],
        summary='Check in a ticket',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
        responses={200: ticket_check_in_response},
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOrganizerOrAdmin])
    def check_in(self, request, pk=None):
        ticket = self.get_object()
        if ticket.status != Ticket.Status.CONFIRMED:
            return Response({'detail': 'Ticket is not valid for check-in.'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = Ticket.Status.USED
        ticket.checked_in_at = timezone.now()
        ticket.save()
        return Response({'detail': 'Check-in successful.', 'ticket': TicketSerializer(ticket).data})
