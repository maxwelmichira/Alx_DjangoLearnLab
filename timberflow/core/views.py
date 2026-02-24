from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'health': '/api/health/',
        'auth': '/api/auth/',
        'suppliers': '/api/suppliers/',
        'procurement': '/api/purchases/',
        'processing': {
            'products': '/api/products/',
            'batches': '/api/batches/',
        },
        'inventory': '/api/inventory/',
        'sales': {
            'customers': '/api/customers/',
            'sales': '/api/sales/',
            'payments': '/api/payments/',
        },
        'finance': {
            'expenses': '/api/expenses/',
            'revenues': '/api/revenues/',
        },
        'analytics': {
            'dashboard': '/api/analytics/dashboard/',
            'profit_and_loss': '/api/analytics/profit-and-loss/',
            'cash_flow': '/api/analytics/cash-flow/',
            'monthly_financials': '/api/analytics/monthly-financials/',
            'sales_trends': '/api/analytics/sales-trends/',
            'product_profitability': '/api/analytics/product-profitability/',
            'customer_insights': '/api/analytics/customer-insights/',
            'supplier_performance': '/api/analytics/supplier-performance/',
            'procurement': '/api/analytics/procurement/',
            'processing': '/api/analytics/processing/',
            'inventory_valuation': '/api/analytics/inventory-valuation/',
        },
        'exports': {
            'sales_csv': '/api/analytics/export/sales-csv/',
            'expenses_csv': '/api/analytics/export/expenses-csv/',
            'pl_pdf': '/api/analytics/export/pl-pdf/',
            'invoice_pdf': '/api/sales/{id}/invoice/',
        },
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok', 'message': 'TimberFlow API is running.'})
