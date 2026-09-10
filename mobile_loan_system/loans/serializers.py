from decimal import Decimal
from rest_framework import serializers
from .models import Loan, EMIPayment


class EMIPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMIPayment
        fields = [
            'id', 'loan', 'installment_number', 'due_date',
            'amount_due', 'amount_paid', 'paid_date', 'status',
        ]
        read_only_fields = ['id', 'loan', 'installment_number', 'due_date', 'amount_due', 'status']


class LoanSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    mobile_display = serializers.CharField(source='mobile.__str__', read_only=True)
    total_paid = serializers.ReadOnlyField()
    outstanding_balance = serializers.ReadOnlyField()
    pending_installments_count = serializers.ReadOnlyField()

    class Meta:
        model = Loan
        fields = [
            'id', 'customer', 'customer_name', 'mobile', 'mobile_display',
            'total_amount', 'down_payment', 'interest_rate', 'tenure_months',
            'loan_amount', 'monthly_emi', 'start_date', 'status',
            'total_paid', 'outstanding_balance', 'pending_installments_count',
            'created_at',
        ]
        read_only_fields = ['id', 'loan_amount', 'monthly_emi', 'status', 'created_at']

    def validate(self, data):
        total_amount = data.get('total_amount')
        down_payment = data.get('down_payment', Decimal('0.00'))
        if down_payment and total_amount and down_payment > total_amount:
            raise serializers.ValidationError("Down payment cannot exceed the total amount.")
        return data


class LoanDetailSerializer(LoanSerializer):
    installments = EMIPaymentSerializer(many=True, read_only=True)

    class Meta(LoanSerializer.Meta):
        fields = LoanSerializer.Meta.fields + ['installments']


class RecordPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    paid_date = serializers.DateField(required=False)
