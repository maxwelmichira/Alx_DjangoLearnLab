from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from datetime import date, timedelta

from procurement.models import TreePurchase
from processing.models import ProcessingBatch, ProcessedProduct
from inventory.models import InventoryItem
from sales.models import Sale, SaleItem
from finance.models import Expense, Revenue


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """High-level business overview."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    total_revenue = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    recent_sales = Sale.objects.filter(sale_date__gte=thirty_days_ago).aggregate(
        total=Sum('total_amount'), count=Count('id')
    )
    low_stock_count = sum(1 for item in InventoryItem.objects.all() if item.is_low_stock)

    return Response({
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': total_revenue - total_expenses,
        'sales_last_30_days': recent_sales['total'] or 0,
        'sales_count_last_30_days': recent_sales['count'] or 0,
        'low_stock_items': low_stock_count,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_financials(request):
    """Monthly revenue vs expenses breakdown."""
    revenue_by_month = (
        Revenue.objects.annotate(month=TruncMonth('revenue_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    expenses_by_month = (
        Expense.objects.annotate(month=TruncMonth('expense_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    return Response({
        'revenue_by_month': list(revenue_by_month),
        'expenses_by_month': list(expenses_by_month),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def procurement_summary(request):
    """Procurement spending by supplier and species."""
    by_supplier = (
        TreePurchase.objects.values('supplier__name')
        .annotate(total_spent=Sum('total_cost'), total_trees=Sum('quantity'))
        .order_by('-total_spent')
    )
    by_species = (
        TreePurchase.objects.values('tree_species')
        .annotate(total_spent=Sum('total_cost'), total_trees=Sum('quantity'))
        .order_by('-total_spent')
    )
    return Response({
        'by_supplier': list(by_supplier),
        'by_species': list(by_species),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def processing_efficiency(request):
    """Processing yield and batch statistics."""
    batches = ProcessingBatch.objects.aggregate(
        total_batches=Count('id'),
        avg_yield=Avg('yield_percentage'),
    )
    top_products = (
        ProcessedProduct.objects.values('product__name', 'product__unit')
        .annotate(total_produced=Sum('quantity_produced'))
        .order_by('-total_produced')[:10]
    )
    return Response({
        'batch_statistics': batches,
        'top_products_by_volume': list(top_products),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_summary(request):
    """Top products by sales volume and revenue."""
    top_by_revenue = (
        SaleItem.objects.values('inventory_item__product__name')
        .annotate(total_revenue=Sum('total_price'), units_sold=Sum('quantity'))
        .order_by('-total_revenue')[:10]
    )
    top_by_volume = (
        SaleItem.objects.values('inventory_item__product__name')
        .annotate(units_sold=Sum('quantity'), total_revenue=Sum('total_price'))
        .order_by('-units_sold')[:10]
    )
    return Response({
        'top_by_revenue': list(top_by_revenue),
        'top_by_volume': list(top_by_volume),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_valuation(request):
    """Current inventory stock levels and estimated value."""
    items = InventoryItem.objects.select_related('product').all()
    data = []
    for item in items:
        data.append({
            'product': item.product.name,
            'category': item.product.get_category_display(),
            'unit': item.product.unit,
            'quantity_in_stock': item.quantity_in_stock,
            'is_low_stock': item.is_low_stock,
            'selling_price': str(item.product.selling_price),
            'estimated_value': str(item.quantity_in_stock * item.product.selling_price),
        })
    total_value = sum(
        item.quantity_in_stock * item.product.selling_price for item in items
    )
    return Response({
        'items': data,
        'total_estimated_value': str(total_value),
    })
