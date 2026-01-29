from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TreePurchaseViewSet

router = DefaultRouter()
router.register(r'purchases', TreePurchaseViewSet, basename='purchase')

urlpatterns = [
    path('', include(router.urls)),
]
