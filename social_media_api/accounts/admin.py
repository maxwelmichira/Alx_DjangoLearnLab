from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin for CustomUser model."""
    
    list_display = ['username', 'email', 'followers_count', 'following_count', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'profile_picture', 'followers')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('bio', 'profile_picture')
        }),
    )
