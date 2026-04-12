from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=300)
    role = models.CharField(max_length=20, choices=[('customer', 'Customer'), ('seller', 'Seller'), ('admin', 'Admin')], default='customer')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

