from django.contrib import admin
from .models import Expense, Revenue

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'category', 'amount', 'expense_date', 'created_by']
    list_filter = ['category']
    search_fields = ['description', 'reference']
    ordering = ['-expense_date']

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['description', 'source', 'amount', 'revenue_date', 'created_by']
    list_filter = ['source']
    search_fields = ['description', 'reference']
    ordering = ['-revenue_date']
