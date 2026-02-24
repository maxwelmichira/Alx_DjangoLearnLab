import csv
import io
from datetime import date, timedelta
from collections import defaultdict

from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from procurement.models import TreePurchase
from processing.models import ProcessingBatch, ProcessedProduct
from inventory.models import InventoryItem
from sales.models import Sale, SaleItem, Payment
from finance.models import Expense, Revenue


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """High-level business overview."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    this_month_start = today.replace(day=1)

    total_revenue = Revenue.objects.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or 0

    recent_sales = Sale.objects.filter(sale_date__gte=thirty_days_ago).aggregate(
        total=Sum('total_amount'), count=Count('id')
    )
    this_month_sales = Sale.objects.filter(sale_date__gte=this_month_start).aggregate(
        total=Sum('total_amount'), count=Count('id')
    )
    low_stock_count = sum(1 for item in InventoryItem.objects.all() if item.is_low_stock)
    pending_payments = Sale.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(total=Sum('total_amount') - Sum('amount_paid'))['total'] or 0

    return Response({
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': total_revenue - total_expenses,
        'this_month': {
            'sales_total': this_month_sales['total'] or 0,
            'sales_count': this_month_sales['count'] or 0,
        },
        'last_30_days': {
            'sales_total': recent_sales['total'] or 0,
            'sales_count': recent_sales['count'] or 0,
        },
        'low_stock_items': low_stock_count,
        'outstanding_balance': pending_payments,
        'active_batches': ProcessingBatch.objects.filter(status='in_progress').count(),
    })


# ─── FINANCIAL REPORTS ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profit_and_loss(request):
    """
    P&L statement. Optional query params: start_date, end_date (YYYY-MM-DD).
    Defaults to current month.
    """
    today = date.today()
    start_date = request.query_params.get('start_date', today.replace(day=1).isoformat())
    end_date = request.query_params.get('end_date', today.isoformat())

    revenue = Revenue.objects.filter(
        revenue_date__gte=start_date, revenue_date__lte=end_date
    )
    expenses = Expense.objects.filter(
        expense_date__gte=start_date, expense_date__lte=end_date
    )

    total_revenue = revenue.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Revenue breakdown by source
    revenue_breakdown = list(
        revenue.values('source').annotate(total=Sum('amount')).order_by('-total')
    )

    # Expense breakdown by category
    expense_breakdown = list(
        expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    )

    # Sales revenue in same period
    sales_revenue = Sale.objects.filter(
        sale_date__gte=start_date, sale_date__lte=end_date
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    return Response({
        'period': {'start': start_date, 'end': end_date},
        'revenue': {
            'total': total_revenue,
            'breakdown': revenue_breakdown,
            'from_sales': sales_revenue,
        },
        'expenses': {
            'total': total_expenses,
            'breakdown': expense_breakdown,
        },
        'gross_profit': sales_revenue - total_expenses,
        'net_profit': total_revenue - total_expenses,
        'profit_margin': round(
            ((total_revenue - total_expenses) / total_revenue * 100), 2
        ) if total_revenue > 0 else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cash_flow(request):
    """
    Cash flow report grouped by day/week/month.
    Query param: period = daily | weekly | monthly (default: monthly)
    """
    period = request.query_params.get('period', 'monthly')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    trunc_map = {
        'daily': TruncDay,
        'weekly': TruncWeek,
        'monthly': TruncMonth,
    }
    trunc_fn = trunc_map.get(period, TruncMonth)

    revenue_qs = Revenue.objects.all()
    expense_qs = Expense.objects.all()
    payment_qs = Payment.objects.all()

    if start_date:
        revenue_qs = revenue_qs.filter(revenue_date__gte=start_date)
        expense_qs = expense_qs.filter(expense_date__gte=start_date)
        payment_qs = payment_qs.filter(payment_date__gte=start_date)
    if end_date:
        revenue_qs = revenue_qs.filter(revenue_date__lte=end_date)
        expense_qs = expense_qs.filter(expense_date__lte=end_date)
        payment_qs = payment_qs.filter(payment_date__lte=end_date)

    inflows = list(
        revenue_qs.annotate(period=trunc_fn('revenue_date'))
        .values('period').annotate(total=Sum('amount')).order_by('period')
    )
    outflows = list(
        expense_qs.annotate(period=trunc_fn('expense_date'))
        .values('period').annotate(total=Sum('amount')).order_by('period')
    )
    payments_received = list(
        payment_qs.annotate(period=trunc_fn('payment_date'))
        .values('period').annotate(total=Sum('amount')).order_by('period')
    )

    return Response({
        'period_type': period,
        'inflows': inflows,
        'outflows': outflows,
        'payments_received': payments_received,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def monthly_financials(request):
    """Monthly revenue vs expenses for the last 12 months."""
    twelve_months_ago = date.today() - timedelta(days=365)

    revenue_by_month = list(
        Revenue.objects.filter(revenue_date__gte=twelve_months_ago)
        .annotate(month=TruncMonth('revenue_date'))
        .values('month').annotate(total=Sum('amount')).order_by('month')
    )
    expenses_by_month = list(
        Expense.objects.filter(expense_date__gte=twelve_months_ago)
        .annotate(month=TruncMonth('expense_date'))
        .values('month').annotate(total=Sum('amount')).order_by('month')
    )

    return Response({
        'revenue_by_month': revenue_by_month,
        'expenses_by_month': expenses_by_month,
    })


# ─── ANALYTICS ───────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_trends(request):
    """Sales trends over time with daily/weekly/monthly grouping."""
    period = request.query_params.get('period', 'monthly')
    trunc_map = {'daily': TruncDay, 'weekly': TruncWeek, 'monthly': TruncMonth}
    trunc_fn = trunc_map.get(period, TruncMonth)

    trends = list(
        Sale.objects.annotate(period=trunc_fn('sale_date'))
        .values('period')
        .annotate(
            total_revenue=Sum('total_amount'),
            total_collected=Sum('amount_paid'),
            count=Count('id')
        )
        .order_by('period')
    )
    return Response({'period_type': period, 'trends': trends})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_profitability(request):
    """Revenue and units sold per product."""
    top_by_revenue = list(
        SaleItem.objects.values('inventory_item__product__name', 'inventory_item__product__category')
        .annotate(
            total_revenue=Sum('total_price'),
            units_sold=Sum('quantity'),
        )
        .order_by('-total_revenue')[:20]
    )
    top_by_volume = list(
        SaleItem.objects.values('inventory_item__product__name', 'inventory_item__product__category')
        .annotate(
            units_sold=Sum('quantity'),
            total_revenue=Sum('total_price'),
        )
        .order_by('-units_sold')[:20]
    )
    return Response({
        'top_by_revenue': top_by_revenue,
        'top_by_volume': top_by_volume,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_insights(request):
    """Customer purchase history and value."""
    top_customers = list(
        Sale.objects.filter(customer__isnull=False)
        .values('customer__name', 'customer__phone')
        .annotate(
            total_purchases=Sum('total_amount'),
            total_paid=Sum('amount_paid'),
            order_count=Count('id'),
        )
        .order_by('-total_purchases')[:20]
    )
    return Response({'top_customers': top_customers})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supplier_performance(request):
    """Supplier spending and delivery stats."""
    performance = list(
        TreePurchase.objects.values('supplier__name', 'supplier__rating')
        .annotate(
            total_spent=Sum('total_cost'),
            total_trees=Sum('quantity'),
            order_count=Count('id'),
        )
        .order_by('-total_spent')
    )
    return Response({'supplier_performance': performance})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def procurement_summary(request):
    """Procurement spending by supplier and species."""
    by_supplier = list(
        TreePurchase.objects.values('supplier__name')
        .annotate(total_spent=Sum('total_cost'), total_trees=Sum('quantity'))
        .order_by('-total_spent')
    )
    by_species = list(
        TreePurchase.objects.values('tree_species')
        .annotate(total_spent=Sum('total_cost'), total_trees=Sum('quantity'))
        .order_by('-total_spent')
    )
    return Response({'by_supplier': by_supplier, 'by_species': by_species})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def processing_efficiency(request):
    """Processing batch statistics and top products by volume."""
    batches = ProcessingBatch.objects.aggregate(
        total_batches=Count('id'),
        completed=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(status='completed')),
        in_progress=Count('id', filter=__import__('django.db.models', fromlist=['Q']).Q(status='in_progress')),
        total_cost=Sum('total_processing_cost'),
    )
    top_products = list(
        ProcessedProduct.objects.values('product__name', 'product__unit')
        .annotate(total_produced=Sum('quantity_produced'))
        .order_by('-total_produced')[:10]
    )
    return Response({
        'batch_statistics': batches,
        'top_products_by_volume': top_products,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_valuation(request):
    """Current inventory stock levels and estimated value."""
    items = InventoryItem.objects.select_related('product').all()
    data = []
    total_value = 0
    for item in items:
        value = item.quantity_in_stock * item.product.selling_price
        total_value += value
        data.append({
            'product': item.product.name,
            'category': item.product.get_category_display(),
            'unit': item.product.unit,
            'quantity_in_stock': item.quantity_in_stock,
            'is_low_stock': item.is_low_stock,
            'selling_price': str(item.product.selling_price),
            'estimated_value': str(value),
        })
    return Response({
        'items': data,
        'total_estimated_value': str(total_value),
    })


# ─── EXPORTS ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_sales_csv(request):
    """Export sales data as CSV."""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    qs = Sale.objects.select_related('customer', 'created_by').all()
    if start_date:
        qs = qs.filter(sale_date__gte=start_date)
    if end_date:
        qs = qs.filter(sale_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice', 'Date', 'Customer', 'Total', 'Paid', 'Balance', 'Status'])
    for sale in qs:
        writer.writerow([
            sale.invoice_number,
            sale.sale_date,
            sale.customer.name if sale.customer else 'Walk-in',
            sale.total_amount,
            sale.amount_paid,
            sale.balance,
            sale.get_payment_status_display(),
        ])
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_expenses_csv(request):
    """Export expenses as CSV."""
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    qs = Expense.objects.all()
    if start_date:
        qs = qs.filter(expense_date__gte=start_date)
    if end_date:
        qs = qs.filter(expense_date__lte=end_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Reference'])
    for expense in qs:
        writer.writerow([
            expense.expense_date,
            expense.get_category_display(),
            expense.description,
            expense.amount,
            expense.reference,
        ])
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_pl_pdf(request):
    """Export P&L report as PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    today = date.today()
    start_date = request.query_params.get('start_date', today.replace(day=1).isoformat())
    end_date = request.query_params.get('end_date', today.isoformat())

    revenue = Revenue.objects.filter(revenue_date__gte=start_date, revenue_date__lte=end_date)
    expenses = Expense.objects.filter(expense_date__gte=start_date, expense_date__lte=end_date)
    total_revenue = revenue.aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_profit = total_revenue - total_expenses

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('title', parent=styles['Title'], alignment=TA_CENTER)
    elements.append(Paragraph("TIMBERFLOW", title_style))
    elements.append(Paragraph("Profit & Loss Statement", styles['Heading2']))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Revenue table
    elements.append(Paragraph("<b>Revenue</b>", styles['Heading3']))
    rev_data = [['Source', 'Amount (KES)']]
    for r in revenue.values('source').annotate(total=Sum('amount')):
        rev_data.append([r['source'].title(), f"{r['total']:,.2f}"])
    rev_data.append(['TOTAL REVENUE', f"{total_revenue:,.2f}"])

    rev_table = Table(rev_data, colWidths=[12*cm, 5*cm])
    rev_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(rev_table)
    elements.append(Spacer(1, 0.5*cm))

    # Expenses table
    elements.append(Paragraph("<b>Expenses</b>", styles['Heading3']))
    exp_data = [['Category', 'Amount (KES)']]
    for e in expenses.values('category').annotate(total=Sum('amount')):
        exp_data.append([e['category'].title(), f"{e['total']:,.2f}"])
    exp_data.append(['TOTAL EXPENSES', f"{total_expenses:,.2f}"])

    exp_table = Table(exp_data, colWidths=[12*cm, 5*cm])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(exp_table)
    elements.append(Spacer(1, 0.5*cm))

    # Net profit
    profit_color = colors.darkgreen if net_profit >= 0 else colors.red
    summary = Table(
        [['NET PROFIT / LOSS', f"KES {net_profit:,.2f}"]],
        colWidths=[12*cm, 5*cm]
    )
    summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), profit_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 13),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary)

    doc.build(elements)
    pdf = buffer.getvalue()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pl_report_{start_date}_{end_date}.pdf"'
    return response
