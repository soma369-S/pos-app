from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterAPIView, LoginAPIView, CustomerProfileViewSet

router = DefaultRouter()
router.register('profiles', CustomerProfileViewSet, basename='customerprofile')

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('', include(router.urls)),
]
