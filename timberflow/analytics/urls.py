from django.urls import path
from .views import (
    dashboard,
    monthly_financials,
    procurement_summary,
    processing_efficiency,
    sales_summary,
    inventory_valuation,
)

urlpatterns = [
    path('analytics/dashboard/', dashboard, name='analytics-dashboard'),
    path('analytics/monthly-financials/', monthly_financials, name='analytics-monthly'),
    path('analytics/procurement/', procurement_summary, name='analytics-procurement'),
    path('analytics/processing/', processing_efficiency, name='analytics-processing'),
    path('analytics/sales/', sales_summary, name='analytics-sales'),
    path('analytics/inventory-valuation/', inventory_valuation, name='analytics-inventory'),
]
