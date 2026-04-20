import csv
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from rest_framework import generics, filters, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, extend_schema,
    extend_schema_view, inline_serializer,
)

from apps.accounts.models import User
from apps.admin_panel.serializers import (
    AdminUserBanSerializer,
    AdminUserListSerializer,
    AdminUserUpdateSerializer,
)
from apps.events.models import Event
from apps.events.serializers import EventListSerializer, EventDetailSerializer, EventCreateUpdateSerializer
from apps.organizer.models import OrganizerProfile
from apps.payments.models import Payment
from apps.tickets.models import Ticket
from utils.permissions import IsAdminUser
from .serializers import (
    AdminOrganizerSerializer,
    AdminOrganizerUpdateSerializer,
    AdminOrganizerStatsSerializer,
)

# ─── Inline schemas ──────────────────────────────────────────────────────────

admin_dashboard_serializer = inline_serializer(
    name='AdminDashboardResponse',
    fields={
        'total_users':        serializers.IntegerField(),
        'total_organizers':   serializers.IntegerField(),
        'total_events':       serializers.IntegerField(),
        'published_events':   serializers.IntegerField(),
        'total_tickets_sold': serializers.IntegerField(),
        'total_revenue':      serializers.DecimalField(max_digits=12, decimal_places=2),
    },
)

system_stats_serializer = inline_serializer(
    name='SystemStatsResponse',
    fields={
        'total_users':          serializers.IntegerField(),
        'total_organizers':     serializers.IntegerField(),
        'total_attendees':      serializers.IntegerField(),
        'total_events':         serializers.IntegerField(),
        'published_events':     serializers.IntegerField(),
        'total_tickets_sold':   serializers.IntegerField(),
        'total_revenue':        serializers.DecimalField(max_digits=12, decimal_places=2),
        'pending_withdrawals':  serializers.IntegerField(),
        'open_support_tickets': serializers.IntegerField(),
        'pending_kyc':          serializers.IntegerField(),
    },
)

event_analytics_serializer = inline_serializer(
    name='EventAnalyticsResponse',
    fields={
        'event': inline_serializer('EventAnalyticsMeta', fields={
            'id': serializers.IntegerField(),
            'title': serializers.CharField(),
            'status': serializers.CharField(),
            'start_date': serializers.DateTimeField(),
            'end_date': serializers.DateTimeField(),
        }),
        'summary': inline_serializer('EventAnalyticsSummary', fields={
            'tickets_sold': serializers.IntegerField(),
            'revenue': serializers.DecimalField(max_digits=12, decimal_places=2),
            'users': serializers.IntegerField(),
        }),
        'timeline': inline_serializer('EventAnalyticsTimeline', fields={
            'labels':       serializers.ListField(child=serializers.CharField()),
            'tickets_sold': serializers.ListField(child=serializers.IntegerField()),
            'revenue':      serializers.ListField(child=serializers.DecimalField(max_digits=12, decimal_places=2)),
            'users':        serializers.ListField(child=serializers.IntegerField()),
        }),
        'ticket_types': serializers.ListField(
            child=inline_serializer('EventAnalyticsTicketType', fields={
                'name':    serializers.CharField(),
                'sold':    serializers.IntegerField(),
                'revenue': serializers.DecimalField(max_digits=12, decimal_places=2),
            }),
        ),
    },
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def build_event_analytics_payload(event):
    sold_statuses = [Ticket.Status.CONFIRMED, Ticket.Status.USED]
    tickets = event.tickets.filter(status__in=sold_statuses)

    timeline_rows = (
        tickets.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(
            tickets_sold=Count('id'),
            revenue=Coalesce(Sum('price_paid'), Decimal('0.00')),
            users=Count('attendee', distinct=True),
        )
        .order_by('day')
    )

    ticket_type_rows = (
        tickets.values('ticket_type__name')
        .annotate(sold=Count('id'), revenue=Coalesce(Sum('price_paid'), Decimal('0.00')))
        .order_by('-sold', 'ticket_type__name')
    )

    labels       = [row['day'].isoformat() for row in timeline_rows]
    ts_sold      = [row['tickets_sold'] for row in timeline_rows]
    revenue_list = [row['revenue'] for row in timeline_rows]
    users_list   = [row['users'] for row in timeline_rows]
    total_revenue = sum((row['revenue'] for row in timeline_rows), Decimal('0.00'))

    return {
        'event': {
            'id': event.id, 'title': event.title,
            'status': event.status,
            'start_date': event.start_date, 'end_date': event.end_date,
        },
        'summary': {
            'tickets_sold': tickets.count(),
            'revenue': total_revenue,
            'users': tickets.values('attendee').distinct().count(),
        },
        'timeline': {
            'labels': labels, 'tickets_sold': ts_sold,
            'revenue': revenue_list, 'users': users_list,
        },
        'ticket_types': [
            {'name': row['ticket_type__name'], 'sold': row['sold'], 'revenue': row['revenue']}
            for row in ticket_type_rows
        ],
    }


# ─── Mixins ──────────────────────────────────────────────────────────────────

class EventAnalyticsAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event.objects.select_related('organizer'), pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        u = self.request.user
        return bool(u.is_authenticated and (u.role == 'admin' or self.event.organizer_id == u.id))

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden('Forbidden.')


class AdminResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ─── Dashboard ───────────────────────────────────────────────────────────────

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'], summary='Admin dashboard metrics',
        description='Returns aggregate statistics for users, events, tickets, and revenue.',
        responses={200: admin_dashboard_serializer},
    )
    def get(self, request):
        completed = Payment.objects.filter(status='completed')
        total_rev = sum(p.amount for p in completed)
        return Response({
            'total_users':        User.objects.count(),
            'total_organizers':   User.objects.filter(role='organizer').count(),
            'total_events':       Event.objects.count(),
            'published_events':   Event.objects.filter(status=Event.Status.APPROVED).count(),
            'total_tickets_sold': Ticket.objects.filter(status='confirmed').count(),
            'total_revenue':      total_rev,
        })


class AdminSystemStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'], summary='Extended system statistics',
        responses={200: system_stats_serializer},
    )
    def get(self, request):
        from apps.payments.models import WithdrawalRequest
        try:
            from apps.support.models import SupportTicket
            open_support = SupportTicket.objects.filter(status='open').count()
        except Exception:
            open_support = 0
        try:
            from apps.kyc.models import KYCDocument
            pending_kyc = KYCDocument.objects.filter(status='pending').count()
        except Exception:
            pending_kyc = 0

        completed = Payment.objects.filter(status='completed')
        total_rev = sum(p.amount for p in completed)

        return Response({
            'total_users':          User.objects.count(),
            'total_organizers':     User.objects.filter(role='organizer').count(),
            'total_attendees':      User.objects.filter(role='attendee').count(),
            'total_events':         Event.objects.count(),
            'published_events':     Event.objects.filter(status=Event.Status.APPROVED).count(),
            'total_tickets_sold':   Ticket.objects.filter(status__in=['confirmed', 'used']).count(),
            'total_revenue':        total_rev,
            'pending_withdrawals':  WithdrawalRequest.objects.filter(status='pending').count(),
            'open_support_tickets': open_support,
            'pending_kyc':          pending_kyc,
        })


# ─── Reports ─────────────────────────────────────────────────────────────────

class AdminRevenueReportView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'], summary='Download revenue CSV report',
        responses={200: OpenApiResponse(description='CSV file')},
    )
    def get(self, request):
        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = 'attachment; filename="revenue_report.csv"'
        writer = csv.writer(resp)
        writer.writerow(['ID', 'User', 'Event', 'Amount', 'Currency', 'Status', 'Provider', 'Date'])
        payments = Payment.objects.select_related('user', 'event').filter(status='completed').order_by('-created_at')
        for p in payments:
            writer.writerow([
                p.id, p.user.email,
                p.event.title if p.event else '—',
                p.amount, p.currency, p.status, p.provider,
                p.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return resp


# ─── Users ───────────────────────────────────────────────────────────────────

class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']
    pagination_class = AdminResultsPagination

    @extend_schema(
        tags=['Admin Panel'],
        summary='List users (admin)',
        parameters=[
            OpenApiParameter('search', str, OpenApiParameter.QUERY, description='Search by email, first name, or last name'),
            OpenApiParameter('role', str, OpenApiParameter.QUERY, description='Filter by attendee, organizer, or admin'),
            OpenApiParameter('status', str, OpenApiParameter.QUERY, description='Filter by active or banned'),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        status_value = self.request.query_params.get('status')
        is_active = self.request.query_params.get('is_active')

        if role in {choice for choice, _ in User.Role.choices}:
            queryset = queryset.filter(role=role)

        if status_value == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_value == 'banned':
            queryset = queryset.filter(is_active=False)
        elif is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset


@extend_schema_view(
    get=extend_schema(tags=['Admin Panel'], summary='Get user (admin)'),
    patch=extend_schema(tags=['Admin Panel'], summary='Update user (admin)'),
    delete=extend_schema(tags=['Admin Panel'], summary='Delete user (admin)'),
)
class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(AdminUserListSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user.pk == user.pk:
            return Response({'detail': 'You cannot deactivate your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserBanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Ban user (admin)',
        request=AdminUserBanSerializer,
        responses={200: AdminUserListSerializer},
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH)],
    )
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user.pk == user.pk:
            return Response({'detail': 'You cannot ban your own account.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdminUserBanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.ban(serializer.validated_data.get('reason', ''))
        return Response(AdminUserListSerializer(user).data)


class AdminUserUnbanView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Unban user (admin)',
        responses={200: AdminUserListSerializer},
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH)],
    )
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.unban()
        return Response(AdminUserListSerializer(user).data)


# ─── Events ──────────────────────────────────────────────────────────────────

class AdminEventListView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Event.objects.select_related('organizer', 'category').all()
        status_value = self.request.query_params.get('status')
        if status_value:
            qs = qs.filter(status=status_value)
        return qs


@extend_schema_view(
    get=extend_schema(tags=['Admin Panel'], summary='Get event (admin)'),
    put=extend_schema(tags=['Admin Panel'], summary='Replace event (admin)'),
    patch=extend_schema(tags=['Admin Panel'], summary='Update event (admin)'),
    delete=extend_schema(tags=['Admin Panel'], summary='Delete event (admin)'),
)
class AdminEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer


class AdminEventModerationView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'], summary='Approve or reject an event',
        description='Admin validates a submitted event. Approved events become published; rejected ones return to draft.',
        request=inline_serializer('EventModeration', fields={
            'action': serializers.ChoiceField(choices=['approve', 'reject']),
            'reason': serializers.CharField(required=False, allow_blank=True),
        }),
        responses={200: EventDetailSerializer()},
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH)],
    )
    def post(self, request, pk):
        from apps.notifications.models import Notification
        from apps.notifications.tasks import create_notification

        event  = get_object_or_404(Event, pk=pk)
        action = request.data.get('action')
        reason = request.data.get('reason', '')

        if action == 'approve':
            event.status = Event.Status.APPROVED
            notif_msg  = f'Your event "{event.title}" has been approved and is now live!'
            notif_type = Notification.Type.EVENT_APPROVED
        elif action == 'reject':
            event.status = Event.Status.REJECTED
            notif_msg  = f'Your event "{event.title}" was not approved. Reason: {reason or "N/A"}'
            notif_type = Notification.Type.EVENT_REJECTED
        else:
            return Response({'detail': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)

        event.save(update_fields=['status', 'updated_at'])
        create_notification(
            recipient=event.organizer,
            notification_type=notif_type,
            title=f'Event {"approved" if action == "approve" else "rejected"}: {event.title}',
            message=notif_msg,
            data={'event_id': event.id},
        )
        return Response(EventDetailSerializer(event).data)


# ─── Analytics ───────────────────────────────────────────────────────────────

class EventAnalyticsDashboardView(EventAnalyticsAccessMixin, TemplateView):
    template_name = 'admin_panel/event_analytics_dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['event'] = self.event
        ctx['analytics_api_url'] = f'/api/admin-panel/events/{self.event.pk}/analytics/data/'
        return ctx


class EventAnalyticsDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Admin Panel'], summary='Event analytics data',
        description='Returns ticket sales, revenue, and attendee analytics for a specific event.',
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH, description='Event ID')],
        responses={200: event_analytics_serializer},
    )
    def get(self, request, pk):
        event = get_object_or_404(Event.objects.select_related('organizer'), pk=pk)
        if request.user.role != 'admin' and event.organizer_id != request.user.id:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(build_event_analytics_payload(event))


# ─── Organizers ────────────────────────────────────────────────────────────────

class AdminOrganizerListView(generics.ListAPIView):
    serializer_class = AdminOrganizerSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['organization_name', 'user__email', 'user__first_name', 'user__last_name']
    pagination_class = AdminResultsPagination

    @extend_schema(
        tags=['Admin Panel'],
        summary='List organizers (admin)',
        parameters=[
            OpenApiParameter('search', str, OpenApiParameter.QUERY),
            OpenApiParameter('is_verified', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = OrganizerProfile.objects.select_related('user').all().order_by('-created_at')
        is_verified = self.request.query_params.get('is_verified')
        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        return queryset


@extend_schema_view(
    get=extend_schema(tags=['Admin Panel'], summary='Get organizer (admin)'),
    patch=extend_schema(tags=['Admin Panel'], summary='Update organizer (admin)'),
    delete=extend_schema(tags=['Admin Panel'], summary='Deactivate organizer account'),
)
class AdminOrganizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrganizerProfile.objects.select_related('user')
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdminOrganizerUpdateSerializer
        return AdminOrganizerSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(AdminOrganizerSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        profile = self.get_object()
        user = profile.user
        if request.user.pk == user.pk:
            return Response({'detail': 'You cannot deactivate your own account.'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminOrganizerStatsView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Get organizer statistics',
        parameters=[OpenApiParameter('pk', int, OpenApiParameter.PATH)],
        responses={200: AdminOrganizerStatsSerializer},
    )
    def get(self, request, pk):
        from decimal import Decimal

        profile = get_object_or_404(OrganizerProfile.objects.select_related('user'), pk=pk)
        user = profile.user

        events = Event.objects.filter(organizer=user)
        tickets = Ticket.objects.filter(
            event__organizer=user, status__in=['confirmed', 'used']
        )

        total_revenue = tickets.aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')

        return Response({
            'total_events': events.count(),
            'published_events': events.filter(status=Event.Status.APPROVED).count(),
            'total_tickets_sold': tickets.count(),
            'total_revenue': total_revenue,
        })


class AdminOrganizerEventsView(generics.ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdminResultsPagination

    @extend_schema(
        tags=['Admin Panel'],
        summary="List organizer's events",
        parameters=[
            OpenApiParameter('pk', int, OpenApiParameter.PATH),
            OpenApiParameter('status', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
        ],
    )
    def get(self, request, pk):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        profile = get_object_or_404(OrganizerProfile, pk=pk)
        qs = Event.objects.filter(organizer=profile.user).select_related('category')
        status_value = self.request.query_params.get('status')
        if status_value:
            qs = qs.filter(status=status_value)
        return qs
