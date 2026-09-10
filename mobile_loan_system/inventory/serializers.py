from rest_framework import serializers
from .models import Supplier, MobilePhone


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'phone', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']


class MobilePhoneSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True, default=None)
    profit_margin = serializers.ReadOnlyField()

    class Meta:
        model = MobilePhone
        fields = [
            'id', 'brand', 'model_name', 'imei_number', 'condition',
            'supplier', 'supplier_name', 'purchase_price', 'purchase_date',
            'selling_price', 'stock_status', 'profit_margin', 'added_at',
        ]
        read_only_fields = ['id', 'added_at']

    def validate_imei_number(self, value):
        if not value.isdigit() or len(value) not in (14, 15, 16):
            raise serializers.ValidationError("IMEI must be a 14-16 digit number.")
        return value
