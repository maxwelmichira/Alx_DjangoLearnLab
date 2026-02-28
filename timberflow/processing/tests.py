from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from suppliers.models import Supplier
from procurement.models import TreePurchase
from .models import Product, ProcessingBatch
import datetime

User = get_user_model()


class ProductTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            name='Round Pole 4 inch',
            category='poles',
            unit='pieces',
            selling_price=500
        )

    def test_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self):
        url = reverse('product-list')
        data = {
            'name': 'Dining Chair',
            'category': 'furniture',
            'unit': 'pieces',
            'selling_price': 8000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_by_category(self):
        url = reverse('product-by-category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProcessingBatchTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name='Test Supplier', contact_person='John',
            phone='0712345678', physical_address='Nairobi', rating=4
        )
        self.purchase = TreePurchase.objects.create(
            supplier=self.supplier, purchase_date=datetime.date.today(),
            invoice_number='INV-001', tree_species='pine', quantity=10,
            unit_cost=5000, average_diameter=8.5, average_length=20.0,
            created_by=self.user
        )
        self.batch = ProcessingBatch.objects.create(
            batch_number='BATCH-001',
            tree_purchase=self.purchase,
            processing_date=datetime.date.today(),
            processed_by=self.user,
            labor_cost=2000,
            equipment_cost=1000,
            other_costs=500
        )

    def test_list_batches(self):
        url = reverse('batch-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_yield_report(self):
        url = reverse('batch-yield-report', args=[self.batch.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('batch_number', response.data)

    def test_statistics(self):
        url = reverse('batch-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_batches', response.data)
