from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """
    CRUD API for customers.

    list:      GET  /api/customers/
    create:    POST /api/customers/
    retrieve:  GET  /api/customers/{id}/
    update:    PUT/PATCH /api/customers/{id}/
    destroy:   DELETE /api/customers/{id}/
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_blacklisted', 'id_proof_type', 'not_active']
    search_fields = ['full_name', 'phone', 'email', 'id_proof_number']
    ordering_fields = ['created_at', 'full_name']

    def get_queryset(self):
        qs = Customer.objects.all()
        # Hide "not_active" customers from the normal list view (used by the
        # frontend Customers page and the loan "pick a customer" dropdown)
        # but still allow retrieving/updating a specific one directly by ID
        # (e.g. from Django admin), so staff can flip the flag back off.
        if self.action == 'list':
            qs = qs.filter(not_active=False)
        return qs