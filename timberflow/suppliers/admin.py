from django.contrib import admin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'rating', 'is_active', 'created_at']
    list_filter = ['is_active', 'rating', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_person', 'phone', 'email')
        }),
        ('Address', {
            'fields': ('physical_address',)
        }),
        ('Rating & Status', {
            'fields': ('rating', 'is_active')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
