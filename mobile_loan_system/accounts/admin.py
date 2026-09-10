from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'city', 'credit_score', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'city', 'id_proof_type')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number', 'id_proof_number')
    readonly_fields = ('created_at', 'updated_at')
