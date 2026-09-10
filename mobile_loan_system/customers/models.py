from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Enter a valid phone number (7-15 digits, optional leading +)."
)


class Customer(models.Model):
    ID_PROOF_CHOICES = [
        ('AADHAAR', 'Aadhaar Card'),
        ('PAN', 'PAN Card'),
        ('VOTER_ID', 'Voter iD'),
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('OTHER', 'Other'),
    ]

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True, validators=[phone_validator])
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)

    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES, default='AADHAAR')
    id_proof_number = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='customers/photos/', blank=True, null=True)

    # Simple credit-worthiness flag staff can toggle before approving a loan
    is_blacklisted = models.BooleanField(default=False)
    not_active = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    @property
    def active_loans_count(self):
        return self.loans.filter(status='ACTIVE').count()
