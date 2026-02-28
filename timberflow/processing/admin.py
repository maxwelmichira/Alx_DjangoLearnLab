from django.contrib import admin
from .models import Product, ProcessingBatch, ProcessedProduct

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'selling_price', 'is_active']
    list_filter = ['category', 'is_active', 'unit']
    search_fields = ['name', 'description']

@admin.register(ProcessingBatch)
class ProcessingBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'tree_purchase', 'processing_date', 'status', 'total_processing_cost']
    list_filter = ['status']
    search_fields = ['batch_number']
    ordering = ['-processing_date']

@admin.register(ProcessedProduct)
class ProcessedProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'processing_batch', 'quantity_produced', 'quality_grade']
    list_filter = ['quality_grade']
    search_fields = ['product__name', 'processing_batch__batch_number']
