from django.contrib import admin
from .models import TreePurchase

@admin.register(TreePurchase)
class TreePurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'tree_species', 'quantity', 'total_cost', 'payment_status', 'purchase_date']
    list_filter = ['tree_species', 'payment_status', 'quality_grade']
    search_fields = ['invoice_number', 'supplier__name']
    ordering = ['-purchase_date']
