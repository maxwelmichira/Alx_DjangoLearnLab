from django.db import models
from django.core.validators import MinValueValidator
from procurement.models import TreePurchase
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    """
    Model for finished timber products
    """
    CATEGORY_CHOICES = [
        ('poles', 'Round Poles'),
        ('offcuts', 'Off-cuts'),
        ('firewood', 'Firewood'),
        ('furniture', 'Furniture'),
    ]
    
    UNIT_CHOICES = [
        ('pieces', 'Pieces'),
        ('bundles', 'Bundles'),
        ('cubic_meters', 'Cubic Meters'),
        ('sets', 'Sets'),
    ]
    
    name = models.CharField(max_length=200, help_text="e.g., Round Pole 4 inch, Dining Chair")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ProcessingBatch(models.Model):
    """
    Model for processing batches - converting trees to products
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    batch_number = models.CharField(max_length=50, unique=True)
    tree_purchase = models.ForeignKey(TreePurchase, on_delete=models.CASCADE, related_name='processing_batches')
    processing_date = models.DateField()
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_batches')
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    equipment_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total_processing_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-processing_date', '-created_at']
        verbose_name = 'Processing Batch'
        verbose_name_plural = 'Processing Batches'
    
    def save(self, *args, **kwargs):
        # Auto-calculate total processing cost
        self.total_processing_cost = self.labor_cost + self.equipment_cost + self.other_costs
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.batch_number} - {self.get_status_display()}"


class ProcessedProduct(models.Model):
    """
    Model for products produced from a processing batch
    """
    GRADE_CHOICES = [
        ('A', 'Grade A - Premium'),
        ('B', 'Grade B - Standard'),
        ('C', 'Grade C - Economy'),
    ]
    
    processing_batch = models.ForeignKey(ProcessingBatch, on_delete=models.CASCADE, related_name='processed_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='produced_items')
    quantity_produced = models.IntegerField(validators=[MinValueValidator(1)])
    quality_grade = models.CharField(max_length=1, choices=GRADE_CHOICES, default='B')
    storage_location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['processing_batch', 'product']
        verbose_name = 'Processed Product'
        verbose_name_plural = 'Processed Products'
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity_produced} {self.product.unit}"
