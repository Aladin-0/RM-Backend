# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser ,  BaseUserManager
from django.contrib.auth.hashers import make_password
from restaurants.models import Restaurant

class StaffUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        CAPTAIN = 'CAPTAIN', 'Captain'
        CHEF = 'CHEF', 'Chef'
        CASHIER = 'CASHIER', 'Cashier'

    # The 'role' field defines the user's job in the system.
    role = models.CharField(max_length=50, choices=Role.choices)
     # this line to link a user to a restaurant
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)

class RoleCredential(models.Model):
    class Role(models.TextChoices):
        # These are the roles that will use shared logins
        CAPTAIN = 'CAPTAIN', 'Captain'
        CHEF = 'CHEF', 'Chef'
        CASHIER = 'CASHIER', 'Cashier'

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='role_credentials')
    role = models.CharField(max_length=50, choices=Role.choices)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128) # This will store the hashed password

    class Meta:
        # Ensure a restaurant can only have one username for each role
        unique_together = ('restaurant', 'role')

    def save(self, *args, **kwargs):
        # Only hash the password if it's not already hashed
        # Django's make_password doesn't rehash if it detects a valid hash
        # But we'll add an extra check to be safe
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant.name} - {self.get_role_display()} Login"