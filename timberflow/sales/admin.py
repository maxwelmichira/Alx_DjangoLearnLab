from django.contrib import admin
from .models import Customer, Sale, SaleItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone', 'email']

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['total_price']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'sale_date', 'total_amount', 'amount_paid', 'payment_status']
    list_filter = ['payment_status', 'payment_method']
    search_fields = ['invoice_number', 'customer__name']
    ordering = ['-sale_date']
    inlines = [SaleItemInline]
