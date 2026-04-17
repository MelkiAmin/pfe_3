from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from utils.permissions import IsAdminUser
from .models import SupportTicket, SupportMessage
from .serializers import SupportTicketSerializer, SupportTicketListSerializer, SupportMessageSerializer

class SupportTicketListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SupportTicketListSerializer
        return SupportTicketSerializer

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

    @extend_schema(tags=['Support'], summary='List my support tickets')
    def get(self, *a, **kw): return super().get(*a, **kw)

    @extend_schema(tags=['Support'], summary='Create a support ticket')
    def post(self, *a, **kw): return super().post(*a, **kw)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SupportTicketDetailView(generics.RetrieveAPIView):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Support'], summary='Get ticket details with messages')
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user).prefetch_related('messages')

class AddMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Support'], summary='Add message to ticket',
        request=SupportMessageSerializer,
        responses={201: SupportMessageSerializer()})
    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)
        msg = SupportMessage.objects.create(
            ticket=ticket, sender=request.user,
            message=request.data.get('message',''),
            is_staff=request.user.role == 'admin'
        )
        return Response(SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED)

class AdminTicketListView(generics.ListAPIView):
    serializer_class = SupportTicketListSerializer
    permission_classes = [IsAdminUser]
    queryset = SupportTicket.objects.select_related('user').all()

    @extend_schema(tags=['Support'], summary='List all tickets (admin)')
    def get_queryset(self):
        qs = super().get_queryset()
        s = self.request.query_params.get('status')
        return qs.filter(status=s) if s else qs

class AdminTicketReplyView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(tags=['Support'], summary='Admin reply + update status',
        request=SupportMessageSerializer,
        responses={200: SupportTicketSerializer()})
    def post(self, request, pk):
        ticket = get_object_or_404(SupportTicket, pk=pk)
        new_status = request.data.get('status')
        msg_text   = request.data.get('message','')
        if msg_text:
            SupportMessage.objects.create(ticket=ticket, sender=request.user, message=msg_text, is_staff=True)
        if new_status and new_status in dict(SupportTicket.Status.choices):
            ticket.status = new_status
            ticket.save(update_fields=['status','updated_at'])
        return Response(SupportTicketSerializer(ticket).data)
