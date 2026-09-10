from django.db import models
from django.contrib.auth.models import User


ID_PROOF_CHOICES = [
    ('AADHAR', 'Aadhar Card'),
    ('PAN', 'PAN Card'),
    ('VOTER', 'Voter ID'),
    ('PASSPORT', 'Passport'),
]


class CustomerProfile(models.Model):
    """
    Extends Django's built-in User model with the extra details
    we need to evaluate someone for a mobile-purchase loan (EMI).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES, default='AADHAR')
    id_proof_number = models.CharField(max_length=50)

    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_score = models.IntegerField(default=650, help_text="Simple internal score used for loan eligibility")
    is_verified = models.BooleanField(default=False, help_text="KYC verified by staff")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    def is_eligible_for_loan(self, requested_amount):
        """Very simple eligibility rule used by the loan workflow."""
        if not self.is_verified:
            return False, "Customer KYC not verified yet."
        if self.credit_score < 500:
            return False, "Credit score too low."
        if self.monthly_income and requested_amount > self.monthly_income * 10:
            return False, "Requested amount too high compared to monthly income."
        return True, "Eligible"
