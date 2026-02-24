from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from .models import Customer, Sale, SaleItem
from .serializers import CustomerSerializer, SaleSerializer, SaleListSerializer, SaleItemSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone', 'email']
    ordering = ['name']


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('customer', 'created_by').prefetch_related('items__inventory_item__product').all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'payment_method', 'customer']
    search_fields = ['invoice_number', 'customer__name']
    ordering_fields = ['sale_date', 'total_amount', 'created_at']
    ordering = ['-sale_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        return SaleSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add an item to a sale"""
        sale = self.get_object()
        serializer = SaleItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save(sale=sale)
            sale.total_amount += item.total_price
            sale.save()
            return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Sales statistics"""
        stats = {
            'total_sales': self.queryset.count(),
            'total_revenue': self.queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'total_collected': self.queryset.aggregate(total=Sum('amount_paid'))['total'] or 0,
            'pending_payment': self.queryset.filter(payment_status='pending').count(),
        }
        return Response(stats)
