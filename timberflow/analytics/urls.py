from django.urls import path
from .views import dashboard, sales_report, procurement_report

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('reports/sales/', sales_report, name='sales-report'),
    path('reports/procurement/', procurement_report, name='procurement-report'),
]
