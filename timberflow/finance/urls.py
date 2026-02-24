from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet, RevenueViewSet

router = DefaultRouter()
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'revenues', RevenueViewSet, basename='revenue')

urlpatterns = [
    path('', include(router.urls)),
]
