from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from processing.models import Product
from .models import InventoryItem

User = get_user_model()


class InventoryTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            name='Round Pole 4 inch', category='poles',
            unit='pieces', selling_price=500
        )
        self.item = InventoryItem.objects.create(
            product=self.product,
            quantity_in_stock=50,
            reorder_level=10
        )

    def test_list_inventory(self):
        url = reverse('inventory-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_low_stock(self):
        self.item.quantity_in_stock = 5
        self.item.save()
        url = reverse('inventory-low-stock')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_adjust_stock_positive(self):
        url = reverse('inventory-adjust-stock', args=[self.item.id])
        response = self.client.post(url, {'quantity': 10, 'reason': 'adjustment'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 60)

    def test_adjust_stock_negative(self):
        url = reverse('inventory-adjust-stock', args=[self.item.id])
        response = self.client.post(url, {'quantity': -20, 'reason': 'sale'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity_in_stock'], 30)
