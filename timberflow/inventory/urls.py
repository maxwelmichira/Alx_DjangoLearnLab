from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'inventory', InventoryItemViewSet, basename='inventory')
router.register(r'stock-movements', StockMovementViewSet, basename='stock-movement')

urlpatterns = [
    path('', include(router.urls)),
]
