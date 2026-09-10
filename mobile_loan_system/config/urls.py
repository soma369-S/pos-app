from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # DRF browsable-api login/logout (handy for testing the API in a browser)
    path('api-auth/', include('rest_framework.urls')),

    # REST API endpoints
    path('api/customers/', include('customers.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/loans/', include('loans.urls')),
    path('api/locations/', include('location.urls')),

    # Server-rendered frontend
    path('', include('frontend.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
