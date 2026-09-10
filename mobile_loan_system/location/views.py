from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location
from .serializers import LocationSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """
    GET  /api/locations/?customer=3   -> all addresses for customer #3
    POST /api/locations/              -> add a new address for a customer
    """
    queryset = Location.objects.select_related('customer').all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'location_type', 'is_primary', 'city', 'state']
    search_fields = ['city', 'state', 'pincode', 'address_line1']
    ordering_fields = ['created_at']