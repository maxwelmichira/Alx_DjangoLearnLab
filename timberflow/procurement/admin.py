from django.contrib import admin
from .models import TreePurchase

@admin.register(TreePurchase)
class TreePurchaseAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'supplier', 'purchase_date', 'tree_species',
        'quantity', 'total_cost', 'quality_grade', 'payment_status'
    ]
    list_filter = ['tree_species', 'quality_grade', 'payment_status', 'purchase_date']
    search_fields = ['invoice_number', 'supplier__name']
    ordering = ['-purchase_date']
    readonly_fields = ['total_cost', 'created_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Supplier Information', {
            'fields': ('supplier', 'invoice_number', 'purchase_date')
        }),
        ('Tree Details', {
            'fields': ('tree_species', 'quantity', 'unit_cost', 'total_cost',
                      'average_diameter', 'average_length', 'quality_grade')
        }),
        ('Delivery & Payment', {
            'fields': ('delivery_date', 'payment_status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
