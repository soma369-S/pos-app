from django.contrib import admin
from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['customer', 'location_type', 'city', 'state', 'pincode', 'is_primary']
    list_filter = ['location_type', 'is_primary', 'state']
    search_fields = ['customer__full_name', 'city', 'pincode', 'address_line1']