from django.db import models
from restaurants.models import Restaurant

# --- NEW: Models for flexible categorization ---
class FoodType(models.Model):
    """ e.g., Veg, Non-Veg, Chicken, Beef """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Cuisine(models.Model):
    """ e.g., Indian, Punjabi, Chinese """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# --- UPDATED: Existing Models ---

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('restaurant', 'name')
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='menu_items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    
    # --- NEW FIELDS ADDED ---
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    food_types = models.ManyToManyField(FoodType, blank=True)
    cuisines = models.ManyToManyField(Cuisine, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MenuItemVariant(models.Model):
    menu_item = models.ForeignKey(MenuItem, related_name='variants', on_delete=models.CASCADE)
    variant_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.name} ({self.variant_name})"

# ... (Bill and OrderItem models remain unchanged)
class Bill(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
    class PaymentMethod(models.TextChoices):
        OFFLINE = 'OFFLINE', 'Offline'
        ONLINE = 'ONLINE', 'Online'
    customer_name = models.CharField(max_length=150)
    table_number = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Bill for {self.customer_name} at Table {self.table_number}"

class OrderItem(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        COMPLETED = 'COMPLETED', 'Completed'
        DECLINED = 'DECLINED', 'Declined'
    bill = models.ForeignKey(Bill, related_name='order_items', on_delete=models.CASCADE)
    variant = models.ForeignKey(MenuItemVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.quantity}x {self.variant.menu_item.name} ({self.variant.variant_name})"
