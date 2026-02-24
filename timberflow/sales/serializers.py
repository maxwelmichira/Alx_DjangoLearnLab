from rest_framework import serializers
from .models import Customer, Sale, SaleItem


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='inventory_item.product.name', read_only=True)
    product_unit = serializers.CharField(source='inventory_item.product.unit', read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'inventory_item', 'product_name', 'product_unit',
            'quantity', 'unit_price', 'total_price'
        ]
        read_only_fields = ['id', 'total_price']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'customer', 'customer_name', 'sale_date', 'invoice_number',
            'payment_method', 'payment_method_display', 'payment_status',
            'payment_status_display', 'total_amount', 'amount_paid', 'balance',
            'notes', 'created_by', 'created_by_username', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class SaleListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'invoice_number', 'customer_name', 'sale_date',
            'total_amount', 'amount_paid', 'balance', 'payment_status_display'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
