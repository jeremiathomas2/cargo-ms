from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Shehena Cargo Management"
admin.site.site_title = "Shehena Admin"
admin.site.index_title = "Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('cargo/', include('cargo.urls')),
    path('packages/', include('packages.urls')),
    path('warehouse/', include('warehouse.urls')),
    path('transportation/', include('transportation.urls')),
    path('gps/', include('gps_tracking.urls')),
    path('delivery/', include('delivery.urls')),
    path('billing/', include('billing.urls')),
    path('payments/', include('payments.urls')),
    path('documents/', include('documents.urls')),
    path('notifications/', include('notifications.urls')),
    path('claims/', include('claims.urls')),
    path('reports/', include('reports.urls')),
    path('customers/', include('customers.urls')),
    path('branches/', include('branches.urls')),
    path('audit/', include('audit.urls')),
    path('settings/', include('self_service.urls')),
    path('track/', include('public_tracking.urls', namespace='public_tracking')),
    path('api/v1/', include('api.urls')),
    path('health/', include('health_check.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
