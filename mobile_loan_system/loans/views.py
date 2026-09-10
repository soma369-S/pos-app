from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Loan, EMIPayment
from .serializers import (
    LoanSerializer, LoanDetailSerializer, EMIPaymentSerializer, RecordPaymentSerializer,
)


class LoanViewSet(viewsets.ModelViewSet):
    """
    CRUD API for loans, plus custom actions:

    GET  /api/loans/{id}/schedule/        -> full EMI schedule for a loan
    POST /api/loans/{id}/pay_installment/ -> record a payment against the
                                              next pending installment
                                              body: {"amount": "1500.00", "paid_date": "2026-09-01"}
    """
    queryset = Loan.objects.select_related('customer', 'mobile').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'customer']
    search_fields = ['customer__full_name', 'mobile__imei_number']
    ordering_fields = ['created_at', 'start_date']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'schedule'):
            return LoanDetailSerializer
        return LoanSerializer

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        loan = self.get_object()
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='pay-installment')
    def pay_installment(self, request, pk=None):
        loan = self.get_object()
        serializer = RecordPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        installment = loan.installments.exclude(status='PAID').order_by('installment_number').first()
        if installment is None:
            return Response(
                {'detail': 'This loan has no pending installments.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        installment.record_payment(
            amount=serializer.validated_data['amount'],
            paid_date=serializer.validated_data.get('paid_date'),
        )
        return Response(EMIPaymentSerializer(installment).data, status=status.HTTP_200_OK)


class EMIPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only listing of installments, useful for a global 'due today' report."""
    queryset = EMIPayment.objects.select_related('loan', 'loan__customer').all()
    serializer_class = EMIPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'loan', 'due_date']
    ordering_fields = ['due_date']
