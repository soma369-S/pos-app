from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction

from customers.models import Customer
from inventory.models import MobilePhone
from .utils import calculate_emi, build_schedule
from django.utils import timezone


class Loan(models.Model):
    """
    A mobile phone sold to a customer on installment (EMI) instead of
    a straight cash sale. One phone -> one loan (OneToOne), since a unit
    once loaned out is no longer available for anyone else.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed / Fully Paid'),
        ('DEFAULTED', 'Defaulted'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='loans')
    mobile = models.OneToOneField(MobilePhone, on_delete=models.PROTECT, related_name='loan')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Phone's selling price")
    down_payment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.00'),
        help_text="Annual interest rate in percent, e.g. 12.00 for 12%"
    )
    tenure_months = models.PositiveIntegerField(help_text="Number of monthly installments")

    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'))
    loan_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, default=Decimal('0.00'),
        help_text="total_amount - down_payment; the amount actually financed"
    )

    start_date = models.DateField(help_text="Date the loan begins / phone handed over")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan #{self.pk} - {self.customer.full_name} - {self.mobile}"

    def clean(self):
        if self.down_payment > self.total_amount:
            raise ValidationError("Down payment cannot exceed the total phone amount.")
        if self.customer.is_blacklisted:
            raise ValidationError("This customer is blacklisted and cannot be given a new loan.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        self.loan_amount = self.total_amount - self.down_payment
        self.monthly_emi = calculate_emi(self.loan_amount, self.interest_rate, self.tenure_months)

        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                # mark the phone as loaned out and build the EMI schedule
                self.mobile.stock_status = 'ON_LOAN'
                self.mobile.save(update_fields=['stock_status'])
                self._generate_schedule()

    def _generate_schedule(self):
        schedule = build_schedule(self.loan_amount, self.interest_rate, self.tenure_months, self.start_date)
        EMIPayment.objects.bulk_create([
            EMIPayment(
                loan=self,
                installment_number=item['installment_number'],
                due_date=item['due_date'],
                amount_due=item['amount_due'],
            )
            for item in schedule
        ])

    # ---- computed helpers used by serializers / templates ----
    @property
    def total_paid(self):
        return self.installments.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or Decimal('0.00')

    @property
    def outstanding_balance(self):
        return (self.loan_amount) - self.total_paid

    @property
    def pending_installments_count(self):
        return self.installments.exclude(status='PAID').count()

    def refresh_status(self):
        """Call after recording a payment to auto-close a fully paid loan."""
        if self.pending_installments_count == 0:
            self.status = 'CLOSED'
            self.save(update_fields=['status'])
            self.mobile.stock_status = 'SOLD'
            self.mobile.save(update_fields=['stock_status'])


class EMIPayment(models.Model):
    """A single scheduled installment for a loan, and its payment record."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('PARTIAL', 'Partially Paid'),
    ]

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    late_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('0.00'),
        help_text="Penalty added once this installment goes overdue."
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['loan', 'installment_number']
        unique_together = ['loan', 'installment_number']

    def __str__(self):
        return f"{self.loan} - Installment {self.installment_number}"
    
    @property
    def days_overdue(self):
        """How many days past due_date this installment currently is (0 if not overdue)."""
        
        if self.status == 'PAID':
            return 0
        today = timezone.localdate()
        if self.due_date >= today:
            return 0
        return (today - self.due_date).days
    def mark_overdue_if_applicable(self):
        if self.status == 'PAID':
            return False

        today = timezone.localdate()
        if self.due_date >= today:
            return False

        days_late = (today - self.due_date).days
        weeks_late = min(days_late // 7, 8)

        flat_fee = Decimal('50.00')
        percentage_fee = (self.amount_due * Decimal('0.01')) * weeks_late
        self.late_fee = (flat_fee + percentage_fee).quantize(Decimal('0.01'))

        was_already_overdue = (self.status == 'OVERDUE')
        self.status = 'OVERDUE'
        self.save(update_fields=['status', 'late_fee'])
        return not was_already_overdue

    def record_payment(self, amount: Decimal, paid_date=None):
        """Apply a payment to this installment, covering the EMI plus any late fee."""
      
        self.amount_paid += Decimal(amount)
        self.paid_date = paid_date or timezone.localdate()

        total_owed = self.amount_due + self.late_fee
        if self.amount_paid >= total_owed:
            self.status = 'PAID'
        elif self.amount_paid > 0:
            self.status = 'PARTIAL'
        self.save()
        self.loan.refresh_status()