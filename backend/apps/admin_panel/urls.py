from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',              views.AdminDashboardView.as_view(),              name='admin-dashboard'),
    path('stats/',                  views.AdminSystemStatsView.as_view(),             name='admin-stats'),
    path('reports/revenue/',        views.AdminRevenueReportView.as_view(),           name='admin-revenue-report'),
    path('users/',                  views.AdminUserListView.as_view(),                name='admin-users'),
    path('users/<int:pk>/',         views.AdminUserDetailView.as_view(),              name='admin-user-detail'),
    path('events/',                 views.AdminEventListView.as_view(),               name='admin-events'),
    path('events/<int:pk>/',        views.AdminEventDetailView.as_view(),             name='admin-event-detail'),
    path('events/<int:pk>/analytics/data/', views.EventAnalyticsDataView.as_view(),  name='event-analytics-data'),
    path('events/<int:pk>/analytics/', views.EventAnalyticsDashboardView.as_view(),  name='event-analytics-dashboard'),
    path('events/<int:pk>/moderate/', views.AdminEventModerationView.as_view(),      name='admin-event-moderate'),
]
