from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, CategoryViewSet, MobileProductViewSet

router = DefaultRouter()
router.register('brands', BrandViewSet, basename='brand')
router.register('categories', CategoryViewSet, basename='category')
router.register('products', MobileProductViewSet, basename='product')

urlpatterns = router.urls
