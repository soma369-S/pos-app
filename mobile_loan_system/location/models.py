from django.db import models


class Location(models.Model):
    """
    A physical address belonging to a customer, kept in its own app so a
    customer can have more than one address (home, work, etc.) and so
    location-specific fields (GPS, pincode, verification) can grow
    independently of the Customer model.
    """
    LOCATION_TYPE_CHOICES = [
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    ]

    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.CASCADE, related_name='locations'
    )
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPE_CHOICES, default='HOME')

    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    is_primary = models.BooleanField(
        default=False, help_text="The main address to use for this customer."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.customer.full_name} - {self.location_type} - {self.city}"

    def save(self, *args, **kwargs):
        # Ensure only one primary address per customer.
        if self.is_primary:
            Location.objects.filter(customer=self.customer, is_primary=True) \
                .exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)