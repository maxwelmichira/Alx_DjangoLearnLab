from rest_framework import serializers
from .models import Product, ProcessingBatch, ProcessedProduct
from procurement.serializers import TreePurchaseListSerializer

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_display', 'unit', 'unit_display',
            'selling_price', 'description', 'image', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing products
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'category_display', 'selling_price', 'unit', 'is_active']


class ProcessedProductSerializer(serializers.ModelSerializer):
    """
    Serializer for ProcessedProduct model
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_unit = serializers.CharField(source='product.unit', read_only=True)
    quality_grade_display = serializers.CharField(source='get_quality_grade_display', read_only=True)
    
    class Meta:
        model = ProcessedProduct
        fields = [
            'id', 'product', 'product_name', 'product_unit',
            'quantity_produced', 'quality_grade', 'quality_grade_display',
            'storage_location', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProcessingBatchSerializer(serializers.ModelSerializer):
    """
    Serializer for ProcessingBatch model
    """
    tree_purchase_details = TreePurchaseListSerializer(source='tree_purchase', read_only=True)
    processed_by_username = serializers.CharField(source='processed_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    processed_products = ProcessedProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProcessingBatch
        fields = [
            'id', 'batch_number', 'tree_purchase', 'tree_purchase_details',
            'processing_date', 'processed_by', 'processed_by_username',
            'labor_cost', 'equipment_cost', 'other_costs', 'total_processing_cost',
            'status', 'status_display', 'notes', 'processed_products',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_processing_cost', 'processed_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the processed_by field to current user
        validated_data['processed_by'] = self.context['request'].user
        return super().create(validated_data)


class ProcessingBatchListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing batches
    """
    tree_species = serializers.CharField(source='tree_purchase.get_tree_species_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ProcessingBatch
        fields = [
            'id', 'batch_number', 'processing_date', 'tree_species',
            'total_processing_cost', 'status_display'
        ]


class ProcessedProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating processed products
    """
    class Meta:
        model = ProcessedProduct
        fields = ['product', 'quantity_produced', 'quality_grade', 'storage_location', 'notes']
