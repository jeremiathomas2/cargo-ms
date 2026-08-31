from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'shipments', views.ShipmentViewSet)
router.register(r'packages', views.PackageViewSet)
router.register(r'customers', views.CustomerViewSet)
router.register(r'vehicles', views.VehicleViewSet)
router.register(r'drivers', views.DriverViewSet)
router.register(r'trips', views.TripViewSet)
router.register(r'manifests', views.ManifestViewSet)
router.register(r'warehouses', views.WarehouseViewSet)
router.register(r'gps-devices', views.GPSDeviceViewSet)
router.register(r'gps-positions', views.GPSPositionViewSet)
router.register(r'deliveries', views.DeliveryViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'claims', views.ClaimViewSet)
router.register(r'branches', views.BranchViewSet)
router.register(r'geofences', views.GeofenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('auth/token/', views.obtain_token, name='token_obtain'),
    path('auth/token/refresh/', views.refresh_token, name='token_refresh'),
    path('public/tracking/<str:tracking_id>/', views.public_tracking_api, name='public_tracking'),
    path('health/', views.health_check, name='health'),
    path('health/db/', views.health_db, name='health_db'),
]
