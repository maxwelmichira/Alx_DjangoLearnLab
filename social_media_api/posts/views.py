from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Comment
from .serializers import PostSerializer, PostListSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer

class FeedView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        # Get all users the current user follows
        following_users = self.request.user.following.all()
        # Return their posts, newest first
        return Post.objects.filter(
            author__in=following_users
        ).order_by('-created_at')
    """
    ViewSet for Post CRUD operations.
    
    Features:
    - List all posts (public)
    - Create post (authenticated users only)
    - Retrieve post details with comments (public)
    - Update post (author only)
    - Delete post (author only)
    - Search by title and content
    - Filter by author
    - Pagination enabled
    """
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use simplified serializer for list view."""
        if self.action == 'list':
            return PostListSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user when creating a post."""
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment CRUD operations.
    
    Features:
    - List all comments (public)
    - Create comment (authenticated users only)
    - Retrieve comment details (public)
    - Update comment (author only)
    - Delete comment (author only)
    - Filter by post
    - Pagination enabled
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def perform_create(self, serializer):
        """Set the author to the current user when creating a comment."""
        serializer.save(author=self.request.user)
