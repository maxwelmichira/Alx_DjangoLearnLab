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
    path('dashboard/', dashboard, name='analytics-dashboard'),
    path('profit-and-loss/', profit_and_loss, name='analytics-pl'),
    path('cash-flow/', cash_flow, name='analytics-cashflow'),
    path('monthly-financials/', monthly_financials, name='analytics-monthly'),
    path('sales-trends/', sales_trends, name='analytics-sales-trends'),
    path('product-profitability/', product_profitability, name='analytics-products'),
    path('customer-insights/', customer_insights, name='analytics-customers'),
    path('supplier-performance/', supplier_performance, name='analytics-suppliers'),
    path('procurement/', procurement_summary, name='analytics-procurement'),
    path('processing/', processing_efficiency, name='analytics-processing'),
    path('inventory-valuation/', inventory_valuation, name='analytics-inventory'),
    path('export/sales-csv/', export_sales_csv, name='export-sales-csv'),
    path('export/expenses-csv/', export_expenses_csv, name='export-expenses-csv'),
    path('export/pl-pdf/', export_pl_pdf, name='export-pl-pdf'),
]
