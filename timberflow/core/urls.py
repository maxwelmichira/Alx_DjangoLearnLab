from django.urls import path
from .views import health_check, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('health/', health_check, name='health-check'),
]
