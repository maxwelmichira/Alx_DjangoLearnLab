from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root - lists all available endpoints."""
    return Response({
        'health': '/api/health/',
        'auth': '/api/auth/',
        'suppliers': '/api/suppliers/',
        'procurement': '/api/purchases/',
        'processing': '/api/batches/',
        'inventory': '/api/inventory/',
        'sales': '/api/sales/',
        'customers': '/api/customers/',
        'expenses': '/api/expenses/',
        'revenues': '/api/revenues/',
        'analytics': {
            'dashboard': '/api/analytics/dashboard/',
            'monthly_financials': '/api/analytics/monthly-financials/',
            'procurement': '/api/analytics/procurement/',
            'processing': '/api/analytics/processing/',
            'sales': '/api/analytics/sales/',
            'inventory_valuation': '/api/analytics/inventory-valuation/',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint."""
    return Response({'status': 'ok', 'message': 'TimberFlow API is running.'})
