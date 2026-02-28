from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from .models import Supplier
from .serializers import SupplierSerializer, SupplierListSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'rating']
    search_fields = ['name', 'contact_person', 'phone']
    ordering_fields = ['name', 'rating', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer

    @action(detail=True, methods=['get'])
    def purchases(self, request, pk=None):
        """Get all purchases from this supplier"""
        from procurement.serializers import TreePurchaseListSerializer
        supplier = self.get_object()
        purchases = supplier.purchases.all()
        return Response({
            'supplier': supplier.name,
            'total_purchases': purchases.count(),
            'total_spent': float(purchases.aggregate(total=Sum('total_cost'))['total'] or 0),
            'purchases': TreePurchaseListSerializer(purchases, many=True).data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Supplier statistics"""
        return Response({
            'total_suppliers': self.queryset.count(),
            'active_suppliers': self.queryset.filter(is_active=True).count(),
            'by_rating': list(
                self.queryset.values('rating').annotate(count=Count('id')).order_by('-rating')
            )
        })
