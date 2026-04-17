from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.KYCSubmitView.as_view(), name='kyc-submit'),
    path('status/', views.KYCStatusView.as_view(), name='kyc-status'),
    path('admin/', views.AdminKYCListView.as_view(), name='kyc-admin-list'),
    path('admin/<int:pk>/action/', views.AdminKYCActionView.as_view(), name='kyc-admin-action'),
]
