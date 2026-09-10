from django.contrib import admin
from .models import Loan, EMIPayment


class EMIPaymentInline(admin.TabularInline):
    model = EMIPayment
    extra = 0
    readonly_fields = ['installment_number', 'due_date', 'amount_due']
    can_delete = False


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer', 'mobile', 'loan_amount', 'monthly_emi',
        'tenure_months', 'status', 'start_date',
    ]
    list_filter = ['status']
    search_fields = ['customer__full_name', 'mobile__imei_number']
    readonly_fields = ['loan_amount', 'monthly_emi']
    inlines = [EMIPaymentInline]


@admin.register(EMIPayment)
class EMIPaymentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'installment_number', 'due_date', 'amount_due', 'amount_paid', 'status']
    list_filter = ['status']
