from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SaleViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]
