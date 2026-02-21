from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]
from django.urls import path
from .views import (
    # your existing imports...
    FollowUserView,
    UnfollowUserView,
)

urlpatterns = [
    # your existing urls...
    path('follow/<int:pk>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/<int:pk>/', UnfollowUserView.as_view(), name='unfollow-user'),
]
