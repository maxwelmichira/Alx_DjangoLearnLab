from rest_framework import serializers
from .models import InventoryItem, StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'inventory_item', 'movement_type', 'movement_type_display',
            'reason', 'reason_display', 'quantity', 'reference',
            'notes', 'created_by', 'created_by_username', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class InventoryItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_category = serializers.CharField(source='product.get_category_display', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    movements = StockMovementSerializer(many=True, read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product', 'product_name', 'product_category', 'product_unit',
            'quantity_in_stock', 'reorder_level', 'is_low_stock',
            'movements', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class InventoryItemListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_category = serializers.CharField(source='product.get_category_display', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'product_name', 'product_category', 'product_unit',
            'quantity_in_stock', 'reorder_level', 'is_low_stock', 'last_updated'
        ]
