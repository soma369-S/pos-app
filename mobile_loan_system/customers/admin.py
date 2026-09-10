from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'id_proof_type', 'is_blacklisted', 'not_active', 'created_at']
    list_filter = ['is_blacklisted', 'not_active', 'id_proof_type']
   # list_editable = ['not_active']
    search_fields = ['full_name', 'phone', 'email', 'id_proof_number']