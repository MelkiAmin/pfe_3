from rest_framework import serializers
from .models import Ticket, TicketType

class TicketTypeSerializer(serializers.ModelSerializer):
    available_quantity = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = TicketType
        fields = ['id', 'event', 'name', 'description', 'price',
                  'quantity', 'quantity_sold', 'available_quantity',
                  'is_available', 'sale_start', 'sale_end']
        read_only_fields = ['quantity_sold']

class TicketSerializer(serializers.ModelSerializer):
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    attendee_name = serializers.CharField(source='attendee.full_name', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'ticket_number', 'ticket_type', 'ticket_type_name',
                  'event', 'event_title', 'attendee', 'attendee_name',
                  'status', 'price_paid', 'qr_code', 'checked_in_at', 'created_at']
        read_only_fields = ['ticket_number', 'attendee', 'qr_code', 'checked_in_at']

class TicketPurchaseSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=10)