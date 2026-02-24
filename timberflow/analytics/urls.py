from django.urls import path
from .views import (
    dashboard,
    profit_and_loss,
    cash_flow,
    monthly_financials,
    sales_trends,
    product_profitability,
    customer_insights,
    supplier_performance,
    procurement_summary,
    processing_efficiency,
    inventory_valuation,
    export_sales_csv,
    export_expenses_csv,
    export_pl_pdf,
)

urlpatterns = [
    path('analytics/dashboard/', dashboard, name='analytics-dashboard'),
    path('analytics/profit-and-loss/', profit_and_loss, name='analytics-pl'),
    path('analytics/cash-flow/', cash_flow, name='analytics-cashflow'),
    path('analytics/monthly-financials/', monthly_financials, name='analytics-monthly'),
    path('analytics/sales-trends/', sales_trends, name='analytics-sales-trends'),
    path('analytics/product-profitability/', product_profitability, name='analytics-products'),
    path('analytics/customer-insights/', customer_insights, name='analytics-customers'),
    path('analytics/supplier-performance/', supplier_performance, name='analytics-suppliers'),
    path('analytics/procurement/', procurement_summary, name='analytics-procurement'),
    path('analytics/processing/', processing_efficiency, name='analytics-processing'),
    path('analytics/inventory-valuation/', inventory_valuation, name='analytics-inventory'),
    path('analytics/export/sales-csv/', export_sales_csv, name='export-sales-csv'),
    path('analytics/export/expenses-csv/', export_expenses_csv, name='export-expenses-csv'),
    path('analytics/export/pl-pdf/', export_pl_pdf, name='export-pl-pdf'),
]
