from decimal import Decimal

from django.db.models import Sum, Count
from rest_framework import generics, permissions, status
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import OrganizerProfile
from .serializers import OrganizerProfileSerializer
from utils.permissions import IsOrganizerOrAdmin

organizer_dashboard_serializer = inline_serializer(
    name='OrganizerDashboardResponse',
    fields={
        'total_events':      serializers.IntegerField(),
        'published_events':  serializers.IntegerField(),
        'draft_events':      serializers.IntegerField(),
        'cancelled_events':  serializers.IntegerField(),
        'total_tickets_sold':serializers.IntegerField(),
        'total_revenue':     serializers.DecimalField(max_digits=12, decimal_places=2),
        'avg_fill_rate':     serializers.FloatField(),
        'recent_events':     serializers.ListField(),
        'top_events':        serializers.ListField(),
    },
)


class OrganizerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = OrganizerProfileSerializer
    permission_classes = [IsOrganizerOrAdmin]

    @extend_schema(tags=['Organizer'], summary='Get / update organizer profile')
    def get_object(self):
        profile, _ = OrganizerProfile.objects.get_or_create(user=self.request.user)
        return profile


class OrganizerListView(generics.ListAPIView):
    queryset = OrganizerProfile.objects.filter(is_verified=True).select_related('user')
    serializer_class = OrganizerProfileSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=['Organizer'], summary='List verified organizers')
    def get(self, *a, **k): return super().get(*a, **k)


class OrganizerDashboardView(APIView):
    permission_classes = [IsOrganizerOrAdmin]

    @extend_schema(
        tags=['Organizer'],
        summary='Organizer dashboard — full metrics',
        description='Returns event counts, revenue, fill rate, top events, and recent events.',
        responses={200: organizer_dashboard_serializer},
    )
    def get(self, request):
        from apps.events.models import Event
        from apps.tickets.models import Ticket
        from apps.events.serializers import EventListSerializer

        events  = Event.objects.filter(organizer=request.user)
        tickets = Ticket.objects.filter(
            event__organizer=request.user, status__in=['confirmed', 'used']
        )

        total_revenue = tickets.aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')

        # Per-event fill rate
        capped = events.exclude(max_capacity__isnull=True).exclude(max_capacity=0)
        fill_rates = []
        for ev in capped:
            sold = Ticket.objects.filter(event=ev, status__in=['confirmed', 'used']).count()
            fill_rates.append(sold / ev.max_capacity * 100)
        avg_fill_rate = round(sum(fill_rates) / len(fill_rates), 1) if fill_rates else 0.0

        # Top 5 events by revenue
        top_events = (
            tickets.values('event__id', 'event__title')
            .annotate(revenue=Sum('price_paid'), sold=Count('id'))
            .order_by('-revenue')[:5]
        )

        recent_events = EventListSerializer(
            events.order_by('-created_at')[:5], many=True
        ).data

        return Response({
            'total_events':       events.count(),
            'published_events':   events.filter(status='published').count(),
            'draft_events':       events.filter(status='draft').count(),
            'cancelled_events':   events.filter(status='cancelled').count(),
            'total_tickets_sold': tickets.count(),
            'total_revenue':      total_revenue,
            'avg_fill_rate':      avg_fill_rate,
            'recent_events':      recent_events,
            'top_events': [
                {
                    'event_id': row['event__id'],
                    'title':    row['event__title'],
                    'revenue':  row['revenue'],
                    'sold':     row['sold'],
                }
                for row in top_events
            ],
        })
