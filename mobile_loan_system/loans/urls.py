from rest_framework.routers import DefaultRouter
from .views import LoanViewSet, EMIPaymentViewSet

router = DefaultRouter()
router.register('installments', EMIPaymentViewSet, basename='emipayment')
router.register('', LoanViewSet, basename='loan')

urlpatterns = router.urls
