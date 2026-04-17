from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('history', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('checkout/', views.CreateCheckoutSessionView.as_view(), name='create-checkout'),
    path('confirm/', views.PaymentConfirmationView.as_view(), name='confirm-payment'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    # Wallet
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('transactions/', views.TransactionListView.as_view(), name='transactions'),
    path('withdrawals/', views.WithdrawalRequestListCreateView.as_view(), name='withdrawals'),
    # Refund
    path('refund/', views.RefundCreateView.as_view(), name='refund-create'),
    # Admin
    path('admin/withdrawals/', views.AdminWithdrawalRequestView.as_view(), name='admin-withdrawals'),
    path('admin/withdrawals/<int:pk>/action/', views.AdminWithdrawalActionView.as_view(), name='admin-withdrawal-action'),
]
