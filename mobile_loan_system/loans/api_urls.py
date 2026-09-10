from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, LoanViewSet, EMIScheduleViewSet, PayEMIAPIView

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('loans', LoanViewSet, basename='loan')
router.register('emi-schedule', EMIScheduleViewSet, basename='emischedule')

urlpatterns = [
    path('emi/<int:pk>/pay/', PayEMIAPIView.as_view(), name='api-pay-emi'),
    path('', include(router.urls)),
]
