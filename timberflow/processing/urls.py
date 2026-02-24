from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProcessingBatchViewSet, ProcessedProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'batches', ProcessingBatchViewSet, basename='batch')
router.register(r'processed-products', ProcessedProductViewSet, basename='processed-product')

urlpatterns = [
    path('', include(router.urls)),
]
