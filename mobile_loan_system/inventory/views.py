from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Supplier, MobilePhone
from .serializers import SupplierSerializer, MobilePhoneSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    search_fields = ['name', 'phone']


class MobilePhoneViewSet(viewsets.ModelViewSet):
    """
    CRUD API for phones purchased into stock.
    Filter examples:
      /api/inventory/phones/?stock_status=AVAILABLE
      /api/inventory/phones/?search=iphone
    """
    queryset = MobilePhone.objects.all()
    serializer_class = MobilePhoneSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_status', 'condition', 'brand', 'supplier']
    search_fields = ['brand', 'model_name', 'imei_number']
    ordering_fields = ['added_at', 'selling_price']
