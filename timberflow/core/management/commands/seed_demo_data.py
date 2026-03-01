from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with demo data for TimberFlow'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding demo data...')

        self.create_users()
        self.create_suppliers()
        self.create_purchases()
        self.create_products()
        self.create_processing_batches()
        self.create_customers()
        self.create_sales()
        self.create_expenses()
        self.create_revenues()

        self.stdout.write(self.style.SUCCESS('✅ Demo data seeded successfully!'))

    def create_users(self):
        from users.models import CustomUser

        users = [
            {'username': 'manager', 'password': 'demo1234', 'email': 'manager@timberflow.com', 'role': 'manager', 'first_name': 'James', 'last_name': 'Kamau'},
            {'username': 'sales1', 'password': 'demo1234', 'email': 'sales@timberflow.com', 'role': 'sales', 'first_name': 'Mary', 'last_name': 'Wanjiku'},
            {'username': 'processor', 'password': 'demo1234', 'email': 'processor@timberflow.com', 'role': 'processor', 'first_name': 'Peter', 'last_name': 'Otieno'},
        ]

        for u in users:
            if not CustomUser.objects.filter(username=u['username']).exists():
                user = CustomUser.objects.create_user(
                    username=u['username'],
                    password=u['password'],
                    email=u['email'],
                    first_name=u['first_name'],
                    last_name=u['last_name'],
                )
                user.role = u['role']
                user.save()
                self.stdout.write(f"  👤 Created user: {u['username']}")

        self.admin = CustomUser.objects.filter(is_superuser=True).first() or CustomUser.objects.first()

    def create_suppliers(self):
        from suppliers.models import Supplier

        suppliers_data = [
            {'name': 'Timber Valley Suppliers', 'contact_person': 'John Kamau', 'phone': '0722334455', 'email': 'john@timbervalley.co.ke', 'physical_address': 'Eldoret, Kenya', 'rating': 4},
            {'name': 'Forest Gold Ltd', 'contact_person': 'Mary Wanjiku', 'phone': '0733445566', 'email': 'mary@forestgold.co.ke', 'physical_address': 'Nakuru, Kenya', 'rating': 5},
            {'name': 'Green Wood Traders', 'contact_person': 'Samuel Omondi', 'phone': '0711223344', 'email': 'samuel@greenwood.co.ke', 'physical_address': 'Kisumu, Kenya', 'rating': 3},
            {'name': 'Highland Timber Co', 'contact_person': 'Grace Njeri', 'phone': '0744556677', 'email': 'grace@highland.co.ke', 'physical_address': 'Nyeri, Kenya', 'rating': 4},
        ]

        self.suppliers = []
        for s in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(name=s['name'], defaults=s)
            self.suppliers.append(supplier)
            if created:
                self.stdout.write(f"  🏭 Created supplier: {s['name']}")

    def create_purchases(self):
        from procurement.models import TreePurchase

        species = ['pine', 'cypress', 'cedar', 'eucalyptus', 'mahogany']
        grades = ['A', 'B', 'C']

        self.purchases = []
        for i in range(12):
            days_ago = random.randint(10, 180)
            purchase_date = date.today() - timedelta(days=days_ago)
            invoice = f'INV-{2025000 + i + 1}'

            if TreePurchase.objects.filter(invoice_number=invoice).exists():
                self.purchases.append(TreePurchase.objects.get(invoice_number=invoice))
                continue

            purchase = TreePurchase.objects.create(
                supplier=random.choice(self.suppliers),
                purchase_date=purchase_date,
                invoice_number=invoice,
                tree_species=random.choice(species),
                quantity=random.randint(20, 100),
                unit_cost=random.randint(800, 2500),
                average_diameter=random.uniform(4, 12),
                average_length=random.uniform(10, 30),
                quality_grade=random.choice(grades),
                delivery_date=purchase_date + timedelta(days=random.randint(1, 7)),
                payment_status=random.choice(['paid', 'paid', 'pending']),
                created_by=self.admin,
            )
            self.purchases.append(purchase)
            self.stdout.write(f"  🌳 Created purchase: {invoice}")

    def create_products(self):
        from processing.models import Product

        products_data = [
            {'name': 'Round Pole 3 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 450},
            {'name': 'Round Pole 4 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 650},
            {'name': 'Round Pole 6 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 950},
            {'name': 'Round Pole 8 inch', 'category': 'poles', 'unit': 'pieces', 'selling_price': 1400},
            {'name': 'Offcut Bundle Small', 'category': 'offcuts', 'unit': 'bundles', 'selling_price': 300},
            {'name': 'Offcut Bundle Large', 'category': 'offcuts', 'unit': 'bundles', 'selling_price': 500},
            {'name': 'Firewood Bundle', 'category': 'firewood', 'unit': 'bundles', 'selling_price': 150},
            {'name': 'Firewood Bag', 'category': 'firewood', 'unit': 'pieces', 'selling_price': 80},
            {'name': 'Dining Chair', 'category': 'furniture', 'unit': 'pieces', 'selling_price': 4500},
            {'name': 'Coffee Table', 'category': 'furniture', 'unit': 'pieces', 'selling_price': 8500},
        ]

        self.products = []
        for p in products_data:
            product, created = Product.objects.get_or_create(name=p['name'], defaults=p)
            self.products.append(product)
            if created:
                self.stdout.write(f"  📦 Created product: {p['name']}")

    def create_processing_batches(self):
        from processing.models import ProcessingBatch, ProcessedProduct
        from inventory.models import InventoryItem, StockMovement

        for i, purchase in enumerate(self.purchases[:8]):
            batch_number = f'BATCH-{2025000 + i + 1}'

            if ProcessingBatch.objects.filter(batch_number=batch_number).exists():
                continue

            batch = ProcessingBatch.objects.create(
                batch_number=batch_number,
                tree_purchase=purchase,
                processing_date=purchase.purchase_date + timedelta(days=random.randint(3, 14)),
                processed_by=self.admin,
                labor_cost=random.randint(5000, 20000),
                equipment_cost=random.randint(2000, 8000),
                other_costs=random.randint(500, 3000),
                status='completed',
            )

            # Add processed products
            selected_products = random.sample(self.products[:6], random.randint(2, 4))
            for product in selected_products:
                qty = random.randint(10, 60)
                ProcessedProduct.objects.create(
                    processing_batch=batch,
                    product=product,
                    quantity_produced=qty,
                    quality_grade=random.choice(['A', 'B', 'B', 'C']),
                )

                # Update inventory
                inventory_item, _ = InventoryItem.objects.get_or_create(
                    product=product,
                    defaults={'quantity_in_stock': 0, 'reorder_level': 10}
                )
                inventory_item.quantity_in_stock += qty
                inventory_item.save()

                StockMovement.objects.create(
                    inventory_item=inventory_item,
                    movement_type='in',
                    reason='processing',
                    quantity=qty,
                    reference=batch_number,
                    created_by=self.admin,
                )

            self.stdout.write(f"  ⚙️  Created batch: {batch_number}")

    def create_customers(self):
        from sales.models import Customer

        customers_data = [
            {'name': 'Nairobi Construction Ltd', 'phone': '0720111222', 'email': 'info@nairobiconstruction.co.ke', 'address': 'Industrial Area, Nairobi'},
            {'name': 'Mombasa Builders', 'phone': '0731222333', 'email': 'info@mombasabuilders.co.ke', 'address': 'Mombasa, Kenya'},
            {'name': 'Rift Valley Contractors', 'phone': '0742333444', 'email': 'info@riftvalley.co.ke', 'address': 'Nakuru, Kenya'},
            {'name': 'John Mutua', 'phone': '0753444555', 'email': 'john.mutua@gmail.com', 'address': 'Machakos, Kenya'},
            {'name': 'Westlands Hardware', 'phone': '0764555666', 'email': 'info@westlandshardware.co.ke', 'address': 'Westlands, Nairobi'},
            {'name': 'Grace Akinyi', 'phone': '0775666777', 'email': 'grace.akinyi@gmail.com', 'address': 'Kisumu, Kenya'},
        ]

        self.customers = []
        for c in customers_data:
            customer, created = Customer.objects.get_or_create(name=c['name'], defaults=c)
            self.customers.append(customer)
            if created:
                self.stdout.write(f"  👥 Created customer: {c['name']}")

    def create_sales(self):
        from sales.models import Sale, SaleItem, Payment
        from inventory.models import InventoryItem, StockMovement

        inventory_items = list(InventoryItem.objects.filter(quantity_in_stock__gt=5))
        if not inventory_items:
            self.stdout.write('  ⚠️  No inventory items available for sales')
            return

        for i in range(15):
            days_ago = random.randint(1, 90)
            sale_date = date.today() - timedelta(days=days_ago)
            invoice = f'SALE-{2025000 + i + 1}'

            if Sale.objects.filter(invoice_number=invoice).exists():
                continue

            customer = random.choice(self.customers)
            sale = Sale.objects.create(
                customer=customer,
                sale_date=sale_date,
                invoice_number=invoice,
                payment_method=random.choice(['cash', 'mpesa', 'bank']),
                payment_status='pending',
                created_by=self.admin,
            )

            total = 0
            selected_items = random.sample(inventory_items, min(random.randint(1, 3), len(inventory_items)))
            for inv_item in selected_items:
                qty = random.randint(1, min(5, inv_item.quantity_in_stock))
                if qty < 1:
                    continue
                unit_price = inv_item.product.selling_price
                item = SaleItem.objects.create(
                    sale=sale,
                    inventory_item=inv_item,
                    quantity=qty,
                    unit_price=unit_price,
                )
                total += item.total_price

                inv_item.quantity_in_stock -= qty
                inv_item.save()

                StockMovement.objects.create(
                    inventory_item=inv_item,
                    movement_type='out',
                    reason='sale',
                    quantity=qty,
                    reference=invoice,
                    created_by=self.admin,
                )

            sale.total_amount = total
            sale.save()

            # Add payment for most sales
            if random.random() > 0.3:
                amount_paid = total if random.random() > 0.3 else float(total) * random.uniform(0.3, 0.8)
                amount_paid = round(amount_paid, 2)
                Payment.objects.create(
                    sale=sale,
                    amount=amount_paid,
                    payment_method=sale.payment_method,
                    payment_date=sale_date + timedelta(days=random.randint(0, 5)),
                    created_by=self.admin,
                )
                sale.amount_paid = amount_paid
                if amount_paid >= total:
                    sale.payment_status = 'paid'
                else:
                    sale.payment_status = 'partial'
                sale.save()

            self.stdout.write(f"  🛒 Created sale: {invoice} - KES {total:,.0f}")

    def create_expenses(self):
        from finance.models import Expense

        categories = ['procurement', 'processing', 'salaries', 'transport', 'equipment', 'utilities', 'maintenance']

        for i in range(20):
            days_ago = random.randint(1, 180)
            Expense.objects.get_or_create(
                reference=f'EXP-{2025000 + i + 1}',
                defaults={
                    'category': random.choice(categories),
                    'description': f'Expense {i + 1}',
                    'amount': random.randint(1000, 50000),
                    'expense_date': date.today() - timedelta(days=days_ago),
                    'created_by': self.admin,
                }
            )
        self.stdout.write('  💸 Created expenses')

    def create_revenues(self):
        from finance.models import Revenue

        for i in range(10):
            days_ago = random.randint(1, 180)
            Revenue.objects.get_or_create(
                reference=f'REV-{2025000 + i + 1}',
                defaults={
                    'source': random.choice(['sales', 'other']),
                    'description': f'Revenue entry {i + 1}',
                    'amount': random.randint(10000, 150000),
                    'revenue_date': date.today() - timedelta(days=days_ago),
                    'created_by': self.admin,
                }
            )
        self.stdout.write('  💰 Created revenues')
