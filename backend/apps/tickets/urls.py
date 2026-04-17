from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('types', views.TicketTypeViewSet, basename='ticket-type')
router.register('', views.TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]