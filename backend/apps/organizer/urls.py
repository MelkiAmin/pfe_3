from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.OrganizerProfileView.as_view(), name='organizer-profile'),
    path('list/', views.OrganizerListView.as_view(), name='organizer-list'),
    path('dashboard/', views.OrganizerDashboardView.as_view(), name='organizer-dashboard'),
]