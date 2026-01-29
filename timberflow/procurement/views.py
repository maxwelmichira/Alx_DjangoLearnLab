from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import TreePurchase
from .serializers import TreePurchaseSerializer, TreePurchaseListSerializer

class TreePurchaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TreePurchase CRUD operations
    """
    queryset = TreePurchase.objects.select_related('supplier', 'created_by').all()
    serializer_class = TreePurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'tree_species', 'quality_grade', 'payment_status']
    search_fields = ['invoice_number', 'supplier__name', 'tree_species']
    ordering_fields = ['purchase_date', 'total_cost', 'created_at']
    ordering = ['-purchase_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TreePurchaseListSerializer
        return TreePurchaseSerializer
    
    @action(detail=False, methods=['get'])
    def pending_payment(self, request):
        """
        Get all purchases with pending payment
        """
        pending = self.queryset.filter(payment_status='pending')
        serializer = self.get_serializer(pending, many=True)
        total_pending = sum(p.total_cost for p in pending)
        
        return Response({
            'count': pending.count(),
            'total_pending_amount': total_pending,
            'purchases': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def by_species(self, request):
        """
        Get purchase statistics by tree species
        """
        from django.db.models import Sum, Count
        
        stats = self.queryset.values('tree_species').annotate(
            total_trees=Sum('quantity'),
            total_spent=Sum('total_cost'),
            purchase_count=Count('id')
        ).order_by('-total_spent')
        
        return Response(stats)
