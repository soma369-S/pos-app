from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, MobilePhoneViewSet

router = DefaultRouter()
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('phones', MobilePhoneViewSet, basename='mobilephone')

urlpatterns = router.urls
