from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Expense, Revenue
import datetime

User = get_user_model()


class FinanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.expense = Expense.objects.create(
            category='salaries',
            description='Monthly salaries',
            amount=50000,
            expense_date=datetime.date.today(),
            created_by=self.user
        )
        self.revenue = Revenue.objects.create(
            source='sales',
            description='Timber sales',
            amount=100000,
            revenue_date=datetime.date.today(),
            created_by=self.user
        )

    def test_list_expenses(self):
        url = reverse('expense-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_expense(self):
        url = reverse('expense-list')
        data = {
            'category': 'transport',
            'description': 'Fuel costs',
            'amount': 5000,
            'expense_date': datetime.date.today()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_revenues(self):
        url = reverse('revenue-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_financial_summary(self):
        url = reverse('revenue-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('net_profit', response.data)
        self.assertEqual(float(response.data['net_profit']), 50000.0)
