from rest_framework import serializers
from .models import TreePurchase
from suppliers.serializers import SupplierListSerializer

class TreePurchaseSerializer(serializers.ModelSerializer):
    """
    Serializer for TreePurchase model
    """
    supplier_details = SupplierListSerializer(source='supplier', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    tree_species_display = serializers.CharField(source='get_tree_species_display', read_only=True)
    quality_grade_display = serializers.CharField(source='get_quality_grade_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = TreePurchase
        fields = [
            'id', 'supplier', 'supplier_details', 'purchase_date', 'invoice_number',
            'tree_species', 'tree_species_display', 'quantity', 'unit_cost', 'total_cost',
            'average_diameter', 'average_length', 'quality_grade', 'quality_grade_display',
            'delivery_date', 'payment_status', 'payment_status_display', 'notes',
            'created_by', 'created_by_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_cost', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the created_by field to current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class TreePurchaseListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing tree purchases
    """
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    tree_species_display = serializers.CharField(source='get_tree_species_display', read_only=True)
    
    class Meta:
        model = TreePurchase
        fields = [
            'id', 'invoice_number', 'supplier_name', 'purchase_date',
            'tree_species_display', 'quantity', 'total_cost', 'payment_status'
        ]
