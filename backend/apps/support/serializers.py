from rest_framework import serializers
from .models import SupportTicket, SupportMessage

class SupportMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    class Meta:
        model = SupportMessage
        fields = ['id','sender_name','message','is_staff','created_at']
        read_only_fields = ['id','sender_name','is_staff','created_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)
    class Meta:
        model = SupportTicket
        fields = ['id','ticket_ref','subject','description','status','priority','messages','created_at','updated_at']
        read_only_fields = ['id','ticket_ref','status','created_at','updated_at']

class SupportTicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['id','ticket_ref','subject','status','priority','created_at','updated_at']
