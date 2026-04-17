from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.SupportTicketListCreateView.as_view(), name='support-list'),
    path('tickets/<int:pk>/', views.SupportTicketDetailView.as_view(), name='support-detail'),
    path('tickets/<int:pk>/message/', views.AddMessageView.as_view(), name='support-message'),
    path('admin/tickets/', views.AdminTicketListView.as_view(), name='support-admin-list'),
    path('admin/tickets/<int:pk>/reply/', views.AdminTicketReplyView.as_view(), name='support-admin-reply'),
]
