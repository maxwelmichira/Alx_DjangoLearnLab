from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    
    Includes author username and handles nested relationships.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.
    
    Includes author information and comment count.
    Can include nested comments if needed.
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'title', 'content',
            'created_at', 'updated_at', 'comments_count', 'comments'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        """Return the number of comments on this post."""
        return obj.comments.count()


class PostListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for post listings (without nested comments).
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'title', 'content',
            'created_at', 'updated_at', 'comments_count'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
