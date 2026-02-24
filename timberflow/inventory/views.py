from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import InventoryItem, StockMovement
from .serializers import (
    InventoryItemSerializer, InventoryItemListSerializer, StockMovementSerializer
)


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related('product').all()
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product__category']
    search_fields = ['product__name']
    ordering_fields = ['quantity_in_stock', 'last_updated']
    ordering = ['product__category', 'product__name']

    def get_serializer_class(self):
        if self.action == 'list':
            return InventoryItemListSerializer
        return InventoryItemSerializer

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        items = [item for item in self.queryset if item.is_low_stock]
        serializer = InventoryItemListSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        quantity = request.data.get('quantity')
        reason = request.data.get('reason', 'adjustment')
        notes = request.data.get('notes', '')

        if not quantity:
            return Response({'error': 'quantity is required'}, status=status.HTTP_400_BAD_REQUEST)

        quantity = int(quantity)
        movement_type = 'in' if quantity > 0 else 'out'

        StockMovement.objects.create(
            inventory_item=item,
            movement_type=movement_type,
            reason=reason,
            quantity=abs(quantity),
            notes=notes,
            created_by=request.user
        )

        item.quantity_in_stock += quantity
        if item.quantity_in_stock < 0:
            item.quantity_in_stock = 0
        item.save()

        serializer = InventoryItemSerializer(item)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related('inventory_item__product', 'created_by').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'reason', 'inventory_item']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
