from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Location
        fields = [
            'id', 'customer', 'customer_name', 'location_type',
            'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country',
            'latitude', 'longitude', 'is_primary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']