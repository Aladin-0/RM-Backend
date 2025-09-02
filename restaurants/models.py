# restaurants/models.py

from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        help_text="Unique URL-friendly name, e.g., 'pizza-palace'"
    )
    address = models.TextField(blank=True)
    
    # Geofence location for this specific restaurant
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_meters = models.PositiveIntegerField(
        default=200, 
        help_text="Geofence radius in meters"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
