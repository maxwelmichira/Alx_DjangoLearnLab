from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from suppliers.models import Supplier
from .models import TreePurchase
import datetime

User = get_user_model()


class TreePurchaseTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John',
            phone='0712345678',
            physical_address='Nairobi',
            rating=4
        )
        self.purchase = TreePurchase.objects.create(
            supplier=self.supplier,
            purchase_date=datetime.date.today(),
            invoice_number='INV-001',
            tree_species='pine',
            quantity=10,
            unit_cost=5000,
            average_diameter=8.5,
            average_length=20.0,
            created_by=self.user
        )

    def test_list_purchases(self):
        url = reverse('purchase-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_purchase(self):
        url = reverse('purchase-list')
        data = {
            'supplier': self.supplier.id,
            'purchase_date': datetime.date.today(),
            'invoice_number': 'INV-002',
            'tree_species': 'cypress',
            'quantity': 5,
            'unit_cost': 4000,
            'average_diameter': 7.0,
            'average_length': 18.0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['invoice_number'], 'INV-002')

    def test_pending_payment(self):
        url = reverse('purchase-pending-payment')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pending_amount', response.data)

    def test_by_species(self):
        url = reverse('purchase-by-species')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
