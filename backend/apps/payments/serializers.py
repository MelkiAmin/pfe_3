from rest_framework import serializers
from .models import Payment, Refund, Wallet, Transaction, WithdrawalRequest


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'event', 'amount', 'currency',
            'status', 'provider', 'provider_payment_id',
            'provider_session_id', 'metadata', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class CheckoutSessionSerializer(serializers.Serializer):
    ticket_type_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=20)
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class PaymentConfirmationSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField(required=False)
    session_id = serializers.CharField(required=False)

    def validate(self, attrs):
        if not attrs.get('payment_id') and not attrs.get('session_id'):
            raise serializers.ValidationError('Either payment_id or session_id is required.')
        return attrs


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'updated_at']
        read_only_fields = ['id', 'balance', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'trx_type', 'details', 'post_balance', 'created_at']
        read_only_fields = ['id', 'amount', 'trx_type', 'details', 'post_balance', 'created_at']


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'amount', 'method', 'account_details',
            'status', 'admin_feedback', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status', 'admin_feedback', 'created_at', 'updated_at']

    def validate_amount(self, value):
        from decimal import Decimal
        if value <= Decimal('0'):
            raise serializers.ValidationError('Withdrawal amount must be positive.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        wallet, _ = Wallet.objects.get_or_create(user=user)
        if wallet.balance < validated_data['amount']:
            raise serializers.ValidationError({'amount': 'Insufficient wallet balance.'})
        return WithdrawalRequest.objects.create(user=user, **validated_data)


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id','payment','amount','reason','provider_refund_id','created_at']
        read_only_fields = ['id','payment','amount','created_at']
