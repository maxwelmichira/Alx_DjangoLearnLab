from django.contrib import admin
from .models import Product, ProcessingBatch, ProcessedProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'selling_price', 'is_active', 'created_at']
    list_filter = ['category', 'unit', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'unit')
        }),
        ('Pricing', {
            'fields': ('selling_price',)
        }),
        ('Details', {
            'fields': ('description', 'image', 'is_active')
        }),
    )


class ProcessedProductInline(admin.TabularInline):
    model = ProcessedProduct
    extra = 1
    fields = ['product', 'quantity_produced', 'quality_grade', 'storage_location']


@admin.register(ProcessingBatch)
class ProcessingBatchAdmin(admin.ModelAdmin):
    list_display = [
        'batch_number', 'tree_purchase', 'processing_date',
        'total_processing_cost', 'status', 'processed_by'
    ]
    list_filter = ['status', 'processing_date', 'tree_purchase__tree_species']
    search_fields = ['batch_number', 'tree_purchase__invoice_number']
    ordering = ['-processing_date']
    readonly_fields = ['total_processing_cost', 'processed_by', 'created_at', 'updated_at']
    inlines = [ProcessedProductInline]
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_number', 'tree_purchase', 'processing_date', 'status')
        }),
        ('Costs', {
            'fields': ('labor_cost', 'equipment_cost', 'other_costs', 'total_processing_cost')
        }),
        ('Processing Details', {
            'fields': ('processed_by', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProcessedProduct)
class ProcessedProductAdmin(admin.ModelAdmin):
    list_display = [
        'processing_batch', 'product', 'quantity_produced',
        'quality_grade', 'storage_location', 'created_at'
    ]
    list_filter = ['quality_grade', 'product__category', 'created_at']
    search_fields = ['product__name', 'processing_batch__batch_number']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('processing_batch', 'product', 'quantity_produced')
        }),
        ('Quality & Storage', {
            'fields': ('quality_grade', 'storage_location')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
    )
