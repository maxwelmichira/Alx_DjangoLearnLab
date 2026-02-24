from django.db import models
from django.core.validators import MinValueValidator
from processing.models import Product, ProcessedProduct
from django.contrib.auth import get_user_model

User = get_user_model()


class InventoryItem(models.Model):
    """
    Tracks current stock levels for each product
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    quantity_in_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product__category', 'product__name']
        verbose_name = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'

    def __str__(self):
        return f"{self.product.name} - {self.quantity_in_stock} {self.product.unit}"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.reorder_level


class StockMovement(models.Model):
    """
    Records every stock in/out movement
    """
    MOVEMENT_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]

    REASON_CHOICES = [
        ('processing', 'From Processing'),
        ('sale', 'Sale'),
        ('damage', 'Damage/Loss'),
        ('return', 'Return'),
        ('adjustment', 'Manual Adjustment'),
    ]

    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_CHOICES)
    reason = models.CharField(max_length=15, choices=REASON_CHOICES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    reference = models.CharField(max_length=100, blank=True, help_text="e.g., batch number or sale ID")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.inventory_item.product.name} ({self.quantity})"
