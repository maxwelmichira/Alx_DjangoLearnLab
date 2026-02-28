from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from procurement.models import TreePurchase
from processing.models import ProcessingBatch, ProcessedProduct
from inventory.models import InventoryItem
from sales.models import Sale
from finance.models import Expense, Revenue


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Main dashboard with key business metrics"""
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
    last_30_days = today - timedelta(days=30)

    # Procurement
    total_trees_purchased = TreePurchase.objects.aggregate(
        total=Sum('quantity'))['total'] or 0
    monthly_procurement_cost = TreePurchase.objects.filter(
        purchase_date__gte=this_month_start
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    # Processing
    batches_in_progress = ProcessingBatch.objects.filter(status='in_progress').count()
    batches_completed = ProcessingBatch.objects.filter(status='completed').count()

    # Inventory
    total_products = InventoryItem.objects.count()
    low_stock_count = sum(1 for item in InventoryItem.objects.all() if item.is_low_stock)

    # Sales
    monthly_sales = Sale.objects.filter(
        sale_date__gte=this_month_start
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    total_sales_count = Sale.objects.count()
    pending_payments = Sale.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Finance
    total_revenue = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_revenue - total_expenses

    return Response({
        'procurement': {
            'total_trees_purchased': total_trees_purchased,
            'monthly_cost': float(monthly_procurement_cost),
        },
        'processing': {
            'batches_in_progress': batches_in_progress,
            'batches_completed': batches_completed,
        },
        'inventory': {
            'total_products': total_products,
            'low_stock_items': low_stock_count,
        },
        'sales': {
            'monthly_revenue': float(monthly_sales),
            'total_sales': total_sales_count,
            'pending_payments': float(pending_payments),
        },
        'finance': {
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_profit': float(net_profit),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):
    """Sales report by period"""
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now().date() - timedelta(days=days)

    sales = Sale.objects.filter(sale_date__gte=start_date)

    return Response({
        'period_days': days,
        'total_sales': sales.count(),
        'total_revenue': float(sales.aggregate(total=Sum('total_amount'))['total'] or 0),
        'total_collected': float(sales.aggregate(total=Sum('amount_paid'))['total'] or 0),
        'by_payment_method': list(
            sales.values('payment_method').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            )
        ),
        'by_payment_status': list(
            sales.values('payment_status').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            )
        ),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def procurement_report(request):
    """Procurement report"""
    purchases = TreePurchase.objects.all()

    return Response({
        'total_purchases': purchases.count(),
        'total_spent': float(purchases.aggregate(total=Sum('total_cost'))['total'] or 0),
        'by_species': list(
            purchases.values('tree_species').annotate(
                count=Count('id'),
                total_trees=Sum('quantity'),
                total_cost=Sum('total_cost')
            )
        ),
        'by_payment_status': list(
            purchases.values('payment_status').annotate(
                count=Count('id'),
                total=Sum('total_cost')
            )
        ),
    })
