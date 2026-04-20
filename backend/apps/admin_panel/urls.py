from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',              views.AdminDashboardView.as_view(),              name='admin-dashboard'),
    path('stats/',                  views.AdminSystemStatsView.as_view(),             name='admin-stats'),
    path('reports/revenue/',        views.AdminRevenueReportView.as_view(),           name='admin-revenue-report'),
    path('users/',                  views.AdminUserListView.as_view(),                name='admin-users'),
    path('users/<int:pk>/',         views.AdminUserDetailView.as_view(),              name='admin-user-detail'),
    path('users/<int:pk>/ban/',     views.AdminUserBanView.as_view(),                 name='admin-user-ban'),
    path('users/<int:pk>/unban/',   views.AdminUserUnbanView.as_view(),               name='admin-user-unban'),
    path('events/',                 views.AdminEventListView.as_view(),               name='admin-events'),
    path('events/<int:pk>/',        views.AdminEventDetailView.as_view(),             name='admin-event-detail'),
    path('events/<int:pk>/analytics/data/', views.EventAnalyticsDataView.as_view(),  name='event-analytics-data'),
    path('events/<int:pk>/analytics/', views.EventAnalyticsDashboardView.as_view(),  name='event-analytics-dashboard'),
    path('events/<int:pk>/moderate/', views.AdminEventModerationView.as_view(),      name='admin-event-moderate'),
    # Organizers
    path('organizers/',              views.AdminOrganizerListView.as_view(),              name='admin-organizers'),
    path('organizers/<int:pk>/',    views.AdminOrganizerDetailView.as_view(),        name='admin-organizer-detail'),
    path('organizers/<int:pk>/stats/', views.AdminOrganizerStatsView.as_view(),        name='admin-organizer-stats'),
    path('organizers/<int:pk>/events/', views.AdminOrganizerEventsView.as_view(),          name='admin-organizer-events'),
]
