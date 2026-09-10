from django.contrib import admin
from .models import Supplier, MobilePhone


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone']
    search_fields = ['name', 'phone']


@admin.register(MobilePhone)
class MobilePhoneAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model_name', 'imei_number', 'condition', 'stock_status', 'selling_price']
    list_filter = ['stock_status', 'condition', 'brand']
    search_fields = ['brand', 'model_name', 'imei_number']
