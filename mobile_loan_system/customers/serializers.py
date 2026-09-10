from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    active_loans_count = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            'id', 'full_name', 'phone', 'email', 'address',
            'id_proof_type', 'id_proof_number', 'photo',
            'is_blacklisted', 'notes',
            'active_loans_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
