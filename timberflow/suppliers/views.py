from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Supplier
from .serializers import SupplierSerializer, SupplierListSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Supplier CRUD operations
    """
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
        """
        Get all purchases from this supplier
        """
        supplier = self.get_object()
        # This will be implemented when we create TreePurchase model
        return Response({
            'supplier': supplier.name,
            'message': 'Purchase history will be available after procurement module is implemented'
        })
