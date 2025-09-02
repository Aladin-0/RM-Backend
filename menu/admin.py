# menu/admin.py

from django.contrib import admin
from .models import Category, MenuItem, MenuItemVariant, Bill, OrderItem, FoodType, Cuisine

@admin.register(FoodType)
class FoodTypeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Cuisine)
class CuisineAdmin(admin.ModelAdmin):
    search_fields = ('name',)

class MenuItemVariantInline(admin.TabularInline):
    model = MenuItemVariant
    fields = ('variant_name', 'price', 'preparation_time')
    extra = 1

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    inlines = [MenuItemVariantInline]
    # Add the new 'is_available' field to the list display
    list_display = ('name', 'category', 'restaurant', 'is_available')
    list_filter = ('restaurant', 'category', 'is_available', 'food_types', 'cuisines')
    search_fields = ('name', 'description')
    
    # This provides a user-friendly two-box interface for the new categories
    filter_horizontal = ('food_types', 'cuisines',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant=request.user.restaurant)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    list_filter = ('restaurant',)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant=request.user.restaurant)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'quantity', 'status')
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'table_number', 'restaurant', 'payment_status', 'created_at')
    list_filter = ('restaurant', 'payment_status', 'created_at')
    inlines = [OrderItemInline]
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(restaurant=request.user.restaurant)

