from django.db import models


class Supplier(models.Model):
    """Who the shop purchases mobile phones from."""
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MobilePhone(models.Model):
    """
    A single physical handset the shop has purchased and holds in stock,
    identified uniquely by its IMEI number.
    """
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('USED', 'Used / Refurbished'),
    ]
    STOCK_STATUS_CHOICES = [
        ('AVAILABLE', 'Available for sale'),
        ('ON_LOAN', 'Given on loan'),
        ('SOLD', 'Sold (cash)'),
        ('RETURNED', 'Returned to supplier'),
    ]

    brand = models.CharField(max_length=80)
    model_name = models.CharField(max_length=120)
    imei_number = models.CharField(max_length=20, unique=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='NEW')

    # Purchasing info - how the shop acquired this unit
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='phones'
    )
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()

    # Selling info
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_status = models.CharField(max_length=10, choices=STOCK_STATUS_CHOICES, default='AVAILABLE')

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.imei_number})"

    @property
    def profit_margin(self):
        return self.selling_price - self.purchase_price
