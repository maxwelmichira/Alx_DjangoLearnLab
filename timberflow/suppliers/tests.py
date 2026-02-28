from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Supplier

User = get_user_model()


class SupplierTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.supplier = Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='0712345678',
            physical_address='Nairobi',
            rating=4
        )

    def test_list_suppliers(self):
        url = reverse('supplier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_supplier(self):
        url = reverse('supplier-list')
        data = {
            'name': 'New Supplier',
            'contact_person': 'Jane Doe',
            'phone': '0798765432',
            'physical_address': 'Mombasa',
            'rating': 3
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Supplier')

    def test_retrieve_supplier(self):
        url = reverse('supplier-detail', args=[self.supplier.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Supplier')

    def test_update_supplier(self):
        url = reverse('supplier-detail', args=[self.supplier.id])
        response = self.client.patch(url, {'rating': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)

    def test_delete_supplier(self):
        url = reverse('supplier-detail', args=[self.supplier.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        url = reverse('supplier-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
