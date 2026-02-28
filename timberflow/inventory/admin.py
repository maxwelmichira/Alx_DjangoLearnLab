from django.contrib import admin
from .models import InventoryItem, StockMovement

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_in_stock', 'reorder_level', 'is_low_stock', 'last_updated']
    list_filter = ['product__category']
    search_fields = ['product__name']

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['inventory_item', 'movement_type', 'reason', 'quantity', 'created_by', 'created_at']
    list_filter = ['movement_type', 'reason']
    search_fields = ['inventory_item__product__name', 'reference']
    ordering = ['-created_at']
