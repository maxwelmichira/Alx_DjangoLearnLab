from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('procurement', 'Tree Procurement'),
        ('processing', 'Processing Costs'),
        ('salaries', 'Salaries'),
        ('transport', 'Transport'),
        ('equipment', 'Equipment'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    expense_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} ({self.expense_date})"


class Revenue(models.Model):
    SOURCE_CHOICES = [
        ('sales', 'Product Sales'),
        ('other', 'Other'),
    ]

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='sales')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    revenue_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='revenues')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-revenue_date']

    def __str__(self):
        return f"{self.get_source_display()} - {self.amount} ({self.revenue_date})"
