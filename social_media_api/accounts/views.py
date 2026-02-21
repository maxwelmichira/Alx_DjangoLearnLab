from rest_framework import generics, permissions
from .models import CustomUser
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /register/
    - Creates new user account
    - Returns user data and authentication token
    - No authentication required
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get the token created in serializer
        token = Token.objects.get(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    API endpoint for user login.
    
    POST /login/
    - Authenticates user credentials
    - Returns user data and authentication token
    - No authentication required
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    
    GET /profile/
    - Returns current user's profile data
    - Requires authentication
    
    PUT/PATCH /profile/
    - Updates current user's profile
    - Requires authentication
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser

class FollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self, request, user_id):
        user_to_follow = self.get_object()

        if user_to_follow == request.user:
            return Response(
                {'error': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.following.add(user_to_follow)
        return Response(
            {'message': f'You are now following {user_to_follow.username}.'},
            status=status.HTTP_200_OK
        )


class UnfollowUserView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self, request, user_id):
        user_to_unfollow = self.get_object()

        if user_to_unfollow == request.user:
            return Response(
                {'error': 'You cannot unfollow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.following.remove(user_to_unfollow)
        return Response(
            {'message': f'You have unfollowed {user_to_unfollow.username}.'},
            status=status.HTTP_200_OK
        )
