from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Customer, Sale
import datetime

User = get_user_model()


class CustomerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(
            name='John Customer', phone='0712345678'
        )

    def test_list_customers(self):
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_customer(self):
        url = reverse('customer-list')
        data = {'name': 'Jane Customer', 'phone': '0798765432'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SaleTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(
            name='John Customer', phone='0712345678'
        )
        self.sale = Sale.objects.create(
            customer=self.customer,
            sale_date=datetime.date.today(),
            invoice_number='SALE-001',
            payment_method='cash',
            total_amount=10000,
            amount_paid=10000,
            payment_status='paid',
            created_by=self.user
        )

    def test_list_sales(self):
        url = reverse('sale-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_sale(self):
        url = reverse('sale-list')
        data = {
            'customer': self.customer.id,
            'sale_date': datetime.date.today(),
            'invoice_number': 'SALE-002',
            'payment_method': 'mpesa',
            'total_amount': 5000,
            'amount_paid': 5000,
            'payment_status': 'paid'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_statistics(self):
        url = reverse('sale-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_sales', response.data)
