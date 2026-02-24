from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from .models import Product, ProcessingBatch, ProcessedProduct
from .serializers import (
    ProductSerializer, ProductListSerializer,
    ProcessingBatchSerializer, ProcessingBatchListSerializer,
    ProcessedProductSerializer, ProcessedProductCreateSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'unit']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'selling_price', 'created_at']
    ordering = ['category', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        from collections import defaultdict
        products = self.queryset.filter(is_active=True)
        grouped = defaultdict(list)
        for product in products:
            grouped[product.get_category_display()].append(
                ProductListSerializer(product).data
            )
        return Response(grouped)


class ProcessingBatchViewSet(viewsets.ModelViewSet):
    queryset = ProcessingBatch.objects.select_related(
        'tree_purchase', 'tree_purchase__supplier', 'processed_by'
    ).prefetch_related('processed_products__product').all()
    serializer_class = ProcessingBatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'tree_purchase__tree_species']
    search_fields = ['batch_number', 'tree_purchase__invoice_number']
    ordering_fields = ['processing_date', 'total_processing_cost', 'created_at']
    ordering = ['-processing_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProcessingBatchListSerializer
        return ProcessingBatchSerializer

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        batch = self.get_object()

        if batch.status == 'completed':
            return Response(
                {'error': 'Cannot add products to a completed batch'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProcessedProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(processing_batch=batch)
            batch_serializer = ProcessingBatchSerializer(batch)
            return Response(batch_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark batch as completed and auto-update inventory."""
        from inventory.models import InventoryItem, StockMovement

        batch = self.get_object()

        if batch.status == 'completed':
            return Response(
                {'error': 'Batch is already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not batch.processed_products.exists():
            return Response(
                {'error': 'Cannot complete batch without any processed products'},
                status=status.HTTP_400_BAD_REQUEST
            )

        batch.status = 'completed'
        batch.save()

        # Auto-update inventory for each processed product
        inventory_updates = []
        for processed in batch.processed_products.all():
            # Get or create inventory item for this product
            inventory_item, created = InventoryItem.objects.get_or_create(
                product=processed.product,
                defaults={'quantity_in_stock': 0, 'reorder_level': 10}
            )

            # Add stock
            inventory_item.quantity_in_stock += processed.quantity_produced
            inventory_item.save()

            # Record stock movement
            StockMovement.objects.create(
                inventory_item=inventory_item,
                movement_type='in',
                reason='processing',
                quantity=processed.quantity_produced,
                reference=batch.batch_number,
                notes=f'From processing batch {batch.batch_number}',
                created_by=request.user
            )

            inventory_updates.append({
                'product': processed.product.name,
                'quantity_added': processed.quantity_produced,
                'new_stock_level': inventory_item.quantity_in_stock,
            })

        serializer = ProcessingBatchSerializer(batch)
        return Response({
            'message': 'Batch completed successfully',
            'batch': serializer.data,
            'inventory_updates': inventory_updates,
        })

    @action(detail=True, methods=['get'])
    def yield_report(self, request, pk=None):
        batch = self.get_object()
        trees_used = batch.tree_purchase.quantity
        products = batch.processed_products.all()

        product_summary = []
        for processed in products:
            product_summary.append({
                'product': processed.product.name,
                'quantity': processed.quantity_produced,
                'unit': processed.product.unit,
                'quality_grade': processed.get_quality_grade_display()
            })

        tree_cost = batch.tree_purchase.total_cost
        processing_cost = batch.total_processing_cost
        total_cost = tree_cost + processing_cost

        return Response({
            'batch_number': batch.batch_number,
            'trees_used': trees_used,
            'tree_species': batch.tree_purchase.get_tree_species_display(),
            'products_produced': product_summary,
            'costs': {
                'tree_procurement': float(tree_cost),
                'labor': float(batch.labor_cost),
                'equipment': float(batch.equipment_cost),
                'other': float(batch.other_costs),
                'total_processing': float(processing_cost),
                'total_cost': float(total_cost)
            },
            'cost_per_tree': float(total_cost / trees_used) if trees_used > 0 else 0
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        stats = {
            'total_batches': self.queryset.count(),
            'in_progress': self.queryset.filter(status='in_progress').count(),
            'completed': self.queryset.filter(status='completed').count(),
            'total_processing_cost': self.queryset.aggregate(
                total=Sum('total_processing_cost')
            )['total'] or 0
        }
        return Response(stats)


class ProcessedProductViewSet(viewsets.ModelViewSet):
    queryset = ProcessedProduct.objects.select_related(
        'processing_batch', 'product'
    ).all()
    serializer_class = ProcessedProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['processing_batch', 'product', 'quality_grade']
    search_fields = ['product__name', 'processing_batch__batch_number']
    ordering_fields = ['created_at', 'quantity_produced']
    ordering = ['-created_at']
