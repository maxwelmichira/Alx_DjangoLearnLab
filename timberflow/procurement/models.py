from django.db import models
from django.core.validators import MinValueValidator
from suppliers.models import Supplier
from django.contrib.auth import get_user_model

User = get_user_model()

class TreePurchase(models.Model):
    """
    Model for recording tree purchases from suppliers
    """
    SPECIES_CHOICES = [
        ('pine', 'Pine'),
        ('cypress', 'Cypress'),
        ('cedar', 'Cedar'),
        ('eucalyptus', 'Eucalyptus'),
        ('mahogany', 'Mahogany'),
        ('oak', 'Oak'),
        ('teak', 'Teak'),
        ('other', 'Other'),
    ]
    
    GRADE_CHOICES = [
        ('A', 'Grade A - Premium'),
        ('B', 'Grade B - Standard'),
        ('C', 'Grade C - Economy'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateField()
    invoice_number = models.CharField(max_length=50, unique=True)
    tree_species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], help_text="Number of trees")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    average_diameter = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Average diameter in inches"
    )
    average_length = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Average length in feet"
    )
    quality_grade = models.CharField(max_length=1, choices=GRADE_CHOICES, default='B')
    delivery_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tree_purchases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-purchase_date', '-created_at']
        verbose_name = 'Tree Purchase'
        verbose_name_plural = 'Tree Purchases'
    
    def save(self, *args, **kwargs):
        # Auto-calculate total_cost
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.get_tree_species_display()} ({self.quantity} trees)"
