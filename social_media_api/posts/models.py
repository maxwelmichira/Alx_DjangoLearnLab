from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    """
    Post model for user-generated content.
    
    Fields:
    - author: ForeignKey to User who created the post
    - title: Post title (max 255 characters)
    - content: Main post content
    - created_at: Timestamp when post was created
    - updated_at: Timestamp when post was last updated
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"


class Comment(models.Model):
    """
    Comment model for post engagement.
    
    Fields:
    - post: ForeignKey to Post being commented on
    - author: ForeignKey to User who created the comment
    - content: Comment text
    - created_at: Timestamp when comment was created
    - updated_at: Timestamp when comment was last updated
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # prevents duplicate likes

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
