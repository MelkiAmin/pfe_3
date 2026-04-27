from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('cart/add/', views.CartAddView.as_view(), name='cart-add'),
]
