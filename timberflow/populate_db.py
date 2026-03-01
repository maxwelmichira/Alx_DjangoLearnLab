#!/usr/bin/env python
"""
Demo data population script for Timberflow API
Run with: python populate_db.py
"""
import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timberflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from suppliers.models import Supplier
from procurement.models import TreePurchase
from processing.models import Product, ProcessingBatch, ProcessedProduct
from inventory.models import InventoryItem, StockMovement
from sales.models import Customer, Sale, SaleItem
from finance.models import Expense, Revenue

User = get_user_model()

print("🌲 Populating Timberflow database with demo data...")

# ── Users ──────────────────────────────────────────────────────────────
print("Creating users...")
admin = User.objects.create_superuser(
    username='admin', email='admin@timberflow.com',
    password='admin1234', role='admin'
) if not User.objects.filter(username='admin').exists() else User.objects.get(username='admin')

manager = User.objects.get_or_create(username='manager', defaults={
    'email': 'manager@timberflow.com', 'role': 'manager',
    'first_name': 'James', 'last_name': 'Mwangi'
})[0]
manager.set_password('manager1234')
manager.save()

sales_staff = User.objects.get_or_create(username='salesstaff', defaults={
    'email': 'sales@timberflow.com', 'role': 'sales',
    'first_name': 'Alice', 'last_name': 'Kamau'
})[0]
sales_staff.set_password('sales1234')
sales_staff.save()

# ── Suppliers ──────────────────────────────────────────────────────────
print("Creating suppliers...")
suppliers_data = [
    {'name': 'Timber Valley Suppliers', 'contact_person': 'John Kamau', 'phone': '0722334455', 'physical_address': 'Eldoret, Kenya', 'rating': 4},
    {'name': 'Forest Gold Ltd', 'contact_person': 'Mary Wanjiku', 'phone': '0733445566', 'physical_address': 'Nakuru, Kenya', 'rating': 5},
    {'name': 'Green Wood Traders', 'contact_person': 'Samuel Omondi', 'phone': '0711223344', 'physical_address': 'Kisumu, Kenya', 'rating': 3},
    {'name': 'Highland Timber Co', 'contact_person': 'Grace Njeri', 'phone': '0744556677', 'physical_address': 'Nyeri, Kenya', 'rating': 4},
]
suppliers = []
for s in suppliers_data:
    obj, _ = Supplier.objects.get_or_create(name=s['name'], defaults=s)
    suppliers.append(obj)

# ── Tree Purchases ─────────────────────────────────────────────────────
print("Creating tree purchases...")
purchases_data = [
    {'supplier': suppliers[0], 'invoice_number': 'INV-2024-001', 'tree_species': 'pine', 'quantity': 50, 'unit_cost': 3500, 'average_diameter': 8.5, 'average_length': 20.0, 'purchase_date': datetime.date(2024, 1, 15), 'payment_status': 'paid'},
    {'supplier': suppliers[1], 'invoice_number': 'INV-2024-002', 'tree_species': 'cypress', 'quantity': 30, 'unit_cost': 4200, 'average_diameter': 7.0, 'average_length': 18.0, 'purchase_date': datetime.date(2024, 2, 10), 'payment_status': 'paid'},
    {'supplier': suppliers[2], 'invoice_number': 'INV-2024-003', 'tree_species': 'eucalyptus', 'quantity': 40, 'unit_cost': 2800, 'average_diameter': 6.5, 'average_length': 15.0, 'purchase_date': datetime.date(2024, 3, 5), 'payment_status': 'pending'},
    {'supplier': suppliers[3], 'invoice_number': 'INV-2024-004', 'tree_species': 'cedar', 'quantity': 20, 'unit_cost': 5500, 'average_diameter': 10.0, 'average_length': 22.0, 'purchase_date': datetime.date(2024, 4, 20), 'payment_status': 'paid'},
]
purchases = []
for p in purchases_data:
    obj, _ = TreePurchase.objects.get_or_create(
        invoice_number=p['invoice_number'],
        defaults={**p, 'created_by': admin}
    )
    purchases.append(obj)

# ── Products ───────────────────────────────────────────────────────────
print("Creating products...")
products_data = [
    {'name': 'Round Pole 4 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 500},
    {'name': 'Round Pole 6 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 800},
    {'name': 'Round Pole 8 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 1200},
    {'name': 'Off-cuts Bundle', 'category': 'offcuts', 'unit': 'bundles', 'selling_price': 300},
    {'name': 'Firewood Bundle', 'category': 'firewood', 'unit': 'bundles', 'selling_price': 150},
    {'name': 'Dining Chair', 'category': 'furniture', 'unit': 'pieces', 'selling_price': 8500},
    {'name': 'Coffee Table', 'category': 'furniture', 'unit': 'pieces', 'selling_price': 15000},
]
products = []
for p in products_data:
    obj, _ = Product.objects.get_or_create(name=p['name'], defaults=p)
    products.append(obj)

# ── Processing Batches ─────────────────────────────────────────────────
print("Creating processing batches...")
batches_data = [
    {'batch_number': 'BATCH-2024-001', 'tree_purchase': purchases[0], 'processing_date': datetime.date(2024, 1, 20), 'labor_cost': 15000, 'equipment_cost': 8000, 'other_costs': 2000, 'status': 'completed'},
    {'batch_number': 'BATCH-2024-002', 'tree_purchase': purchases[1], 'processing_date': datetime.date(2024, 2, 15), 'labor_cost': 12000, 'equipment_cost': 6000, 'other_costs': 1500, 'status': 'completed'},
    {'batch_number': 'BATCH-2024-003', 'tree_purchase': purchases[2], 'processing_date': datetime.date(2024, 3, 10), 'labor_cost': 10000, 'equipment_cost': 5000, 'other_costs': 1000, 'status': 'in_progress'},
]
batches = []
for b in batches_data:
    obj, _ = ProcessingBatch.objects.get_or_create(
        batch_number=b['batch_number'],
        defaults={**b, 'processed_by': manager}
    )
    batches.append(obj)

# ── Processed Products ─────────────────────────────────────────────────
print("Creating processed products...")
processed_data = [
    {'processing_batch': batches[0], 'product': products[0], 'quantity_produced': 100, 'quality_grade': 'A'},
    {'processing_batch': batches[0], 'product': products[1], 'quantity_produced': 60, 'quality_grade': 'B'},
    {'processing_batch': batches[0], 'product': products[3], 'quantity_produced': 30, 'quality_grade': 'B'},
    {'processing_batch': batches[1], 'product': products[2], 'quantity_produced': 40, 'quality_grade': 'A'},
    {'processing_batch': batches[1], 'product': products[4], 'quantity_produced': 50, 'quality_grade': 'C'},
]
for p in processed_data:
    ProcessedProduct.objects.get_or_create(
        processing_batch=p['processing_batch'],
        product=p['product'],
        defaults=p
    )

# ── Inventory ──────────────────────────────────────────────────────────
print("Creating inventory...")
inventory_data = [
    {'product': products[0], 'quantity_in_stock': 80, 'reorder_level': 20},
    {'product': products[1], 'quantity_in_stock': 45, 'reorder_level': 15},
    {'product': products[2], 'quantity_in_stock': 30, 'reorder_level': 10},
    {'product': products[3], 'quantity_in_stock': 8, 'reorder_level': 10},  # low stock
    {'product': products[4], 'quantity_in_stock': 5, 'reorder_level': 15},  # low stock
    {'product': products[5], 'quantity_in_stock': 12, 'reorder_level': 5},
    {'product': products[6], 'quantity_in_stock': 6, 'reorder_level': 3},
]
inventory_items = []
for i in inventory_data:
    obj, _ = InventoryItem.objects.get_or_create(product=i['product'], defaults=i)
    inventory_items.append(obj)

# ── Customers ──────────────────────────────────────────────────────────
print("Creating customers...")
customers_data = [
    {'name': 'Nairobi Hardware Ltd', 'phone': '0720111222', 'email': 'info@nairobihdw.co.ke', 'address': 'Nairobi CBD'},
    {'name': 'BuildRight Construction', 'phone': '0731222333', 'email': 'orders@buildright.co.ke', 'address': 'Westlands, Nairobi'},
    {'name': 'John Mwenda', 'phone': '0742333444', 'email': '', 'address': 'Thika'},
    {'name': 'Mombasa Timber Yard', 'phone': '0753444555', 'email': 'buy@mombsatimber.co.ke', 'address': 'Mombasa'},
]
customers = []
for c in customers_data:
    obj, _ = Customer.objects.get_or_create(name=c['name'], defaults=c)
    customers.append(obj)

# ── Sales ──────────────────────────────────────────────────────────────
print("Creating sales...")
sales_data = [
    {'customer': customers[0], 'invoice_number': 'SALE-2024-001', 'sale_date': datetime.date(2024, 2, 1), 'payment_method': 'bank', 'payment_status': 'paid', 'total_amount': 75000, 'amount_paid': 75000},
    {'customer': customers[1], 'invoice_number': 'SALE-2024-002', 'sale_date': datetime.date(2024, 2, 15), 'payment_method': 'mpesa', 'payment_status': 'paid', 'total_amount': 42000, 'amount_paid': 42000},
    {'customer': customers[2], 'invoice_number': 'SALE-2024-003', 'sale_date': datetime.date(2024, 3, 1), 'payment_method': 'cash', 'payment_status': 'paid', 'total_amount': 18500, 'amount_paid': 18500},
    {'customer': customers[3], 'invoice_number': 'SALE-2024-004', 'sale_date': datetime.date(2024, 3, 20), 'payment_method': 'credit', 'payment_status': 'pending', 'total_amount': 95000, 'amount_paid': 0},
]
sales = []
for s in sales_data:
    obj, _ = Sale.objects.get_or_create(
        invoice_number=s['invoice_number'],
        defaults={**s, 'created_by': sales_staff}
    )
    sales.append(obj)

# ── Expenses ───────────────────────────────────────────────────────────
print("Creating expenses...")
expenses_data = [
    {'category': 'salaries', 'description': 'January staff salaries', 'amount': 85000, 'expense_date': datetime.date(2024, 1, 31)},
    {'category': 'transport', 'description': 'Fuel for delivery trucks', 'amount': 12000, 'expense_date': datetime.date(2024, 2, 10)},
    {'category': 'equipment', 'description': 'Chainsaw maintenance', 'amount': 8500, 'expense_date': datetime.date(2024, 2, 20)},
    {'category': 'utilities', 'description': 'Electricity bill', 'amount': 6000, 'expense_date': datetime.date(2024, 3, 5)},
    {'category': 'maintenance', 'description': 'Workshop repairs', 'amount': 15000, 'expense_date': datetime.date(2024, 3, 15)},
]
for e in expenses_data:
    Expense.objects.get_or_create(
        description=e['description'],
        defaults={**e, 'created_by': admin}
    )

# ── Revenue ────────────────────────────────────────────────────────────
print("Creating revenue records...")
revenues_data = [
    {'source': 'sales', 'description': 'February sales revenue', 'amount': 117000, 'revenue_date': datetime.date(2024, 2, 28)},
    {'source': 'sales', 'description': 'March sales revenue', 'amount': 113500, 'revenue_date': datetime.date(2024, 3, 31)},
    {'source': 'other', 'description': 'Equipment rental income', 'amount': 25000, 'revenue_date': datetime.date(2024, 3, 20)},
]
for r in revenues_data:
    Revenue.objects.get_or_create(
        description=r['description'],
        defaults={**r, 'created_by': admin}
    )

print("")
print("✅ Demo data created successfully!")
print("")
print("👤 Login credentials:")
print("   Admin:    username=admin      password=admin1234")
print("   Manager:  username=manager    password=manager1234")
print("   Sales:    username=salesstaff password=sales1234")
print("")
print(f"📦 Created:")
print(f"   {User.objects.count()} users")
print(f"   {Supplier.objects.count()} suppliers")
print(f"   {TreePurchase.objects.count()} tree purchases")
print(f"   {Product.objects.count()} products")
print(f"   {ProcessingBatch.objects.count()} processing batches")
print(f"   {InventoryItem.objects.count()} inventory items")
print(f"   {Customer.objects.count()} customers")
print(f"   {Sale.objects.count()} sales")
print(f"   {Expense.objects.count()} expenses")
print(f"   {Revenue.objects.count()} revenue records")
