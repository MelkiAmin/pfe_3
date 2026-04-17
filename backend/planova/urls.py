from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('api/schema/',  SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',    SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',   SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/',       admin.site.urls),
    path('api/',         include('apps.core.urls')),
    path('api/auth/',    include('apps.accounts.urls')),
    path('api/events/',  include('apps.events.urls')),
    path('api/organizer/', include('apps.organizer.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/admin-panel/', include('apps.admin_panel.urls')),
    path('api/kyc/',     include('apps.kyc.urls')),
    path('api/support/', include('apps.support.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
