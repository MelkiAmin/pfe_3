from decimal import Decimal

import stripe
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    OpenApiParameter, OpenApiResponse, extend_schema,
    extend_schema_view, inline_serializer,
)

from .models import Payment, Refund, Wallet, Transaction, WithdrawalRequest
from .serializers import (
    PaymentSerializer,
    CheckoutSessionSerializer,
    PaymentConfirmationSerializer,
    WalletSerializer,
    TransactionSerializer,
    WithdrawalRequestSerializer,
    RefundSerializer,
)


def get_stripe():
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    return stripe


# ─── Inline response schemas ────────────────────────────────────────────────

checkout_session_response_serializer = inline_serializer(
    name='CheckoutSessionResponse',
    fields={
        'session_id': serializers.CharField(),
        'checkout_url': serializers.URLField(),
        'payment_id': serializers.IntegerField(),
    },
)

stripe_webhook_response_serializer = inline_serializer(
    name='StripeWebhookResponse',
    fields={'status': serializers.CharField()},
)

payment_confirmation_response_serializer = inline_serializer(
    name='PaymentConfirmationResponse',
    fields={
        'payment': PaymentSerializer(),
        'stripe_status': serializers.CharField(),
        'payment_status': serializers.CharField(),
        'fulfilled': serializers.BooleanField(),
    },
)

withdrawal_action_serializer = inline_serializer(
    name='WithdrawalAction',
    fields={
        'action': serializers.ChoiceField(choices=['approve', 'reject']),
        'admin_feedback': serializers.CharField(required=False, allow_blank=True),
    },
)


# ─── Helpers ────────────────────────────────────────────────────────────────

def sync_payment_from_checkout_session(payment, session):
    from apps.notifications.models import Notification
    from apps.notifications.tasks import create_notification, send_order_confirmation_email
    from apps.tickets.models import TicketType, Ticket

    stripe_status = session.get('status')
    stripe_payment_status = session.get('payment_status')

    if stripe_payment_status != 'paid':
        if stripe_status == 'expired':
            payment.status = Payment.Status.FAILED
        payment.metadata = {
            **payment.metadata,
            'stripe_status': stripe_status,
            'stripe_payment_status': stripe_payment_status,
        }
        payment.save(update_fields=['status', 'metadata', 'updated_at'])
        return False

    with transaction.atomic():
        payment = Payment.objects.select_for_update().get(pk=payment.pk)

        if payment.status == Payment.Status.COMPLETED:
            return True

        metadata = session.get('metadata', {}) or payment.metadata
        ticket_type = TicketType.objects.select_for_update().get(id=metadata['ticket_type_id'])
        quantity = int(metadata.get('quantity', 1))

        payment.status = Payment.Status.COMPLETED
        payment.provider_payment_id = session.get('payment_intent', '') or session.get('id', '')
        payment.metadata = {
            **payment.metadata,
            'stripe_status': stripe_status,
            'stripe_payment_status': stripe_payment_status,
            'fulfilled_quantity': quantity,
        }
        payment.save(update_fields=['status', 'provider_payment_id', 'metadata', 'updated_at'])

        created_tickets = []
        for _ in range(quantity):
            ticket = Ticket.objects.create(
                ticket_type=ticket_type,
                event=ticket_type.event,
                attendee=payment.user,
                status=Ticket.Status.CONFIRMED,
                price_paid=ticket_type.price,
            )
            ticket.attach_qr_code()
            created_tickets.append(ticket)

        ticket_type.quantity_sold += quantity
        ticket_type.save(update_fields=['quantity_sold'])

        event = ticket_type.event
        if event.tickets_available >= quantity:
            event.tickets_available -= quantity
            event.save(update_fields=['tickets_available'])

        # Credit organizer wallet
        organizer = ticket_type.event.organizer
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=organizer)
        commission_rate = Decimal(str(getattr(settings, 'ORGANIZER_COMMISSION', '1')))
        commission = payment.amount * commission_rate
        wallet.balance += commission
        wallet.save(update_fields=['balance', 'updated_at'])
        Transaction.objects.create(
            user=organizer,
            amount=commission,
            trx_type=Transaction.TrxType.CREDIT,
            details=f'Ticket sales for event #{ticket_type.event_id} ({quantity} ticket(s))',
            post_balance=wallet.balance,
        )

    create_notification(
        recipient=payment.user,
        notification_type=Notification.Type.PAYMENT_CONFIRMED,
        title='Payment confirmed',
        message=f'Your payment for "{payment.event.title}" was confirmed and {quantity} ticket(s) were issued.',
        data={
            'payment_id': payment.id,
            'session_id': payment.provider_session_id,
            'tickets': [str(t.ticket_number) for t in created_tickets],
        },
    )

    send_order_confirmation_email.delay(payment.id)
    return True


# ─── Views ───────────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(tags=['Payments'], summary='List my payments'),
    retrieve=extend_schema(
        tags=['Payments'], summary='Retrieve a payment',
        parameters=[OpenApiParameter('id', int, OpenApiParameter.PATH)],
    ),
)
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'admin':
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Payments'],
        summary='Create a Stripe checkout session',
        description='Validates ticket availability, creates a Stripe Checkout session, and stores a pending payment record.',
        request=CheckoutSessionSerializer,
        responses={
            200: checkout_session_response_serializer,
            400: OpenApiResponse(description='Stripe error or invalid quantity'),
            404: OpenApiResponse(description='Ticket type not found'),
        },
    )
    def post(self, request):
        stripe_client = get_stripe()
        serializer = CheckoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from apps.tickets.models import TicketType
        from django.utils import timezone

        ticket_type = get_object_or_404(TicketType, id=serializer.validated_data['ticket_type_id'])
        quantity = serializer.validated_data['quantity']
        event = ticket_type.event

        if event.status != 'approved':
            return Response({'detail': 'Event is not approved.'}, status=status.HTTP_400_BAD_REQUEST)

        if event.start_date <= timezone.now():
            return Response({'detail': 'Event has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        if event.tickets_available < quantity:
            return Response({'detail': 'Not enough tickets available.'}, status=status.HTTP_400_BAD_REQUEST)

        if ticket_type.available_quantity < quantity:
            return Response({'detail': 'Not enough tickets available for this ticket type.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            metadata = {
                'user_id': str(request.user.id),
                'ticket_type_id': str(ticket_type.id),
                'quantity': str(quantity),
            }
            session = stripe_client.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': getattr(settings, 'STRIPE_CURRENCY', 'usd'),
                        'product_data': {'name': f'{ticket_type.event.title} — {ticket_type.name}'},
                        'unit_amount': int(ticket_type.price * 100),
                    },
                    'quantity': quantity,
                }],
                mode='payment',
                success_url=serializer.validated_data['success_url'],
                cancel_url=serializer.validated_data['cancel_url'],
                client_reference_id=str(request.user.id),
                customer_email=request.user.email,
                metadata=metadata,
            )

            payment = Payment.objects.create(
                user=request.user,
                event=ticket_type.event,
                amount=ticket_type.price * quantity,
                currency=getattr(settings, 'STRIPE_CURRENCY', 'usd').upper(),
                provider=Payment.Provider.STRIPE,
                provider_session_id=session.id,
                status=Payment.Status.PENDING,
                metadata=metadata,
            )

            return Response({
                'session_id': session.id,
                'checkout_url': session.url,
                'payment_id': payment.id,
            })

        except stripe.error.StripeError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Stripe checkout error: {str(e)}', exc_info=True)
            return Response({'detail': 'Erreur de paiement. Veuillez réessayer.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Checkout error: {str(e)}', exc_info=True)
            return Response({'detail': 'Erreur serveur. Veuillez réessayer.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentConfirmationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Payments'],
        summary='Confirm a Stripe payment',
        request=PaymentConfirmationSerializer,
        responses={200: payment_confirmation_response_serializer},
    )
    def post(self, request):
        serializer = PaymentConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = self._get_payment(request, serializer.validated_data)
        stripe_client = get_stripe()

        try:
            session = stripe_client.checkout.Session.retrieve(payment.provider_session_id)
        except stripe.error.StripeError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        fulfilled = sync_payment_from_checkout_session(payment, session)
        payment.refresh_from_db()

        return Response({
            'payment': PaymentSerializer(payment).data,
            'stripe_status': session.get('status', ''),
            'payment_status': session.get('payment_status', ''),
            'fulfilled': fulfilled,
        })

    def _get_payment(self, request, data):
        qs = Payment.objects.all() if getattr(request.user, 'role', None) == 'admin' \
            else Payment.objects.filter(user=request.user)
        if data.get('payment_id'):
            return get_object_or_404(qs, pk=data['payment_id'])
        return get_object_or_404(qs, provider_session_id=data['session_id'])


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Payments'],
        summary='Stripe webhook endpoint',
        request=None,
        responses={200: stripe_webhook_response_serializer},
    )
    def post(self, request):
        stripe_client = get_stripe()
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe_client.Webhook.construct_event(
                payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', ''),
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event_type = event['type']
        event_object = event['data']['object']

        if event_type in {'checkout.session.completed', 'checkout.session.async_payment_succeeded'}:
            self._handle_checkout_complete(event_object)
        elif event_type in {'checkout.session.async_payment_failed', 'checkout.session.expired'}:
            self._handle_checkout_failure(event_object, event_type)

        return Response({'status': 'ok'})

    def _handle_checkout_complete(self, session):
        try:
            payment = Payment.objects.get(provider_session_id=session['id'])
        except Payment.DoesNotExist:
            return
        sync_payment_from_checkout_session(payment, session)

    def _handle_checkout_failure(self, session, event_type):
        try:
            payment = Payment.objects.get(provider_session_id=session['id'])
        except Payment.DoesNotExist:
            return
        payment.status = Payment.Status.FAILED
        payment.metadata = {**payment.metadata, 'failure_event': event_type}
        payment.save(update_fields=['status', 'metadata', 'updated_at'])


# ─── Wallet Views ─────────────────────────────────────────────────────────────

class WalletView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Payments'],
        summary='Get my wallet balance',
        responses={200: WalletSerializer()},
    )
    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return Response(WalletSerializer(wallet).data)


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'], summary='List my transactions')
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class WithdrawalRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Payments'], summary='List / create withdrawal requests')
    def get_queryset(self):
        return WithdrawalRequest.objects.filter(user=self.request.user)


class AdminWithdrawalRequestView(generics.ListAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Admin Panel'], summary='List all withdrawal requests (admin)')
    def get_queryset(self):
        if self.request.user.role != 'admin':
            return WithdrawalRequest.objects.none()
        return WithdrawalRequest.objects.select_related('user').all()


class AdminWithdrawalActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Admin Panel'],
        summary='Approve or reject a withdrawal request',
        request=withdrawal_action_serializer,
        responses={
            200: WithdrawalRequestSerializer(),
            400: OpenApiResponse(description='Insufficient balance or invalid action'),
            403: OpenApiResponse(description='Admin only'),
        },
    )
    def post(self, request, pk):
        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        wr = get_object_or_404(WithdrawalRequest, pk=pk)
        if wr.status != WithdrawalRequest.Status.PENDING:
            return Response({'detail': 'Withdrawal already processed.'}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action')
        feedback = request.data.get('admin_feedback', '')

        if action == 'approve':
            with transaction.atomic():
                wallet = get_object_or_404(Wallet.objects.select_for_update(), user=wr.user)
                if wallet.balance < wr.amount:
                    return Response({'detail': 'User has insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)
                wallet.balance -= wr.amount
                wallet.save(update_fields=['balance', 'updated_at'])
                Transaction.objects.create(
                    user=wr.user, amount=wr.amount, trx_type=Transaction.TrxType.DEBIT,
                    details=f'Withdrawal approved #{wr.id}', post_balance=wallet.balance,
                )
            wr.status = WithdrawalRequest.Status.APPROVED

        elif action == 'reject':
            wr.status = WithdrawalRequest.Status.REJECTED

        else:
            return Response({'detail': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)

        wr.admin_feedback = feedback
        wr.save(update_fields=['status', 'admin_feedback', 'updated_at'])
        return Response(WithdrawalRequestSerializer(wr).data)


from .models import Refund
from .serializers import RefundSerializer

class RefundCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['Payments'], summary='Request a refund for a completed payment',
        request=inline_serializer('RefundRequest', fields={
            'payment_id': serializers.IntegerField(),
            'reason': serializers.CharField(),
        }),
        responses={
            201: RefundSerializer(),
            400: OpenApiResponse(description='Already refunded or payment not completed'),
        },
    )
    def post(self, request):
        payment_id = request.data.get('payment_id')
        reason = request.data.get('reason', '')

        payment = get_object_or_404(Payment, pk=payment_id, user=request.user)
        if payment.status != Payment.Status.COMPLETED:
            return Response({'detail': 'Only completed payments can be refunded.'}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(payment, 'refund'):
            return Response({'detail': 'Payment already refunded.'}, status=status.HTTP_400_BAD_REQUEST)

        # Cancel associated tickets
        from apps.tickets.models import Ticket
        Ticket.objects.filter(
            event=payment.event, attendee=request.user, status=Ticket.Status.CONFIRMED
        ).update(status=Ticket.Status.REFUNDED)

        refund = Refund.objects.create(payment=payment, amount=payment.amount, reason=reason)
        payment.status = Payment.Status.REFUNDED
        payment.save(update_fields=['status', 'updated_at'])

        return Response(RefundSerializer(refund).data, status=status.HTTP_201_CREATED)
