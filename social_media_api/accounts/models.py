from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Additional Fields:
    - bio: Text field for user biography/description
    - profile_picture: Image field for user avatar
    - followers: ManyToMany relationship for following system
    
    The followers field creates a self-referential relationship where:
    - Users can follow other users
    - symmetrical=False means following is not mutual (like Twitter, not Facebook)
    - related_name='following' allows reverse lookup of who a user follows
    """
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )
    
    def __str__(self):
        return self.username
    
    @property
    def followers_count(self):
        """Return the number of followers."""
        return self.followers.count()
    
    @property
    def following_count(self):
        """Return the number of users this user follows."""
        return self.following.count()
