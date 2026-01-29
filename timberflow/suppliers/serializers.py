from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for Supplier model
    """
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'phone', 'email',
            'physical_address', 'rating', 'is_active', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class SupplierListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing suppliers
    """
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'phone', 'rating', 'is_active']
