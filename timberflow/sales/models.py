from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import InventoryItem
from django.contrib.auth import get_user_model

User = get_user_model()


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('credit', 'Credit'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    sale_date = models.DateField()
    invoice_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sale_date', '-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.total_amount}"

    @property
    def balance(self):
        return self.total_amount - self.amount_paid

    def update_payment_status(self):
        """Auto-update payment status based on amount paid."""
        if self.amount_paid <= 0:
            self.payment_status = 'pending'
        elif self.amount_paid >= self.total_amount:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='sale_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    class Meta:
        ordering = ['sale']

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.inventory_item.product.name} x {self.quantity}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, help_text="e.g., M-Pesa transaction code")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"Payment of {self.amount} for {self.sale.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate amount_paid on the sale
        total_paid = self.sale.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.sale.amount_paid = total_paid
        self.sale.update_payment_status()
