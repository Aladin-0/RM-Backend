# menu/serializers.py

from rest_framework import serializers
from .models import Category, MenuItem, MenuItemVariant, Bill, OrderItem , FoodType, Cuisine, Category

# --- Read-Only Serializers (for displaying the menu) ---

class MenuItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemVariant
        fields = ['variant_name', 'price']

class MenuItemSerializer(serializers.ModelSerializer):
    variants = MenuItemVariantSerializer(many=True, read_only=True)
    class Meta:
        model = MenuItem
        fields = ['name', 'variants']

class CategorySerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['name', 'menu_items']

# --- Write-Only Serializers (for creating orders) ---

class OrderItemWriteSerializer(serializers.ModelSerializer):
    """
    This serializer is ONLY for validating the items in a NEW order.
    """
    variant_id = serializers.IntegerField()
    class Meta:
        model = OrderItem
        fields = ['variant_id', 'quantity']

class BillSerializer(serializers.ModelSerializer):
    """
    This serializer is ONLY for creating a NEW bill.
    """
    # This field uses the correct "Write" serializer and is write_only.
    order_items = OrderItemWriteSerializer(many=True, write_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'customer_name', 'table_number', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        bill = Bill.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(
                bill=bill,
                variant_id=item_data['variant_id'],
                quantity=item_data['quantity']
            )
        return bill

class CashierOrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='variant.menu_item.name', read_only=True)
    variant_name = serializers.CharField(source='variant.variant_name', read_only=True)
    price = serializers.DecimalField(source='variant.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['name', 'variant_name', 'quantity', 'price']

# This serializer formats the entire bill, including its items and total price
class CashierBillSerializer(serializers.ModelSerializer):
    order_items = CashierOrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id', 'customer_name', 'table_number', 'payment_status', 'created_at', 'order_items', 'total_price']

    def get_total_price(self, bill):
        # This method calculates the total price by summing up all items
        return sum(item.variant.price * item.quantity for item in bill.order_items.all())

class MenuItemVariantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemVariant
        fields = ['variant_name', 'price', 'preparation_time']

class MenuItemManageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Restaurant Admin to manage their menu items.
    """
    # We include the variants for detailed viewing and writing
    variants = MenuItemVariantWriteSerializer(many=True, required=False)

    class Meta:
        model = MenuItem
        # These are all the fields the owner can see or edit
        fields = [
            'id', 'name', 'description', 'category', 'is_available', 
            'food_types', 'cuisines', 'variants'
        ]
        read_only_fields = ['id'] # The ID cannot be edited
        
    def create(self, validated_data):
        variants_data = validated_data.pop('variants', [])
        menu_item = MenuItem.objects.create(**validated_data)
        
        # Create variants for the menu item
        for variant_data in variants_data:
            MenuItemVariant.objects.create(menu_item=menu_item, **variant_data)
            
        return menu_item
        
    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', [])
        
        # Update the menu item fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.is_available = validated_data.get('is_available', instance.is_available)
        
        # Handle many-to-many relationships
        if 'food_types' in validated_data:
            instance.food_types.set(validated_data.get('food_types'))
        if 'cuisines' in validated_data:
            instance.cuisines.set(validated_data.get('cuisines'))
            
        instance.save()
        
        # If variants are provided, replace the existing ones
        if variants_data:
            instance.variants.all().delete()
            for variant_data in variants_data:
                MenuItemVariant.objects.create(menu_item=instance, **variant_data)
                
        return instance

class PublicMenuItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemVariant
        fields = ['variant_name', 'price', 'preparation_time']

class PublicMenuItemSerializer(serializers.ModelSerializer):
    variants = PublicMenuItemVariantSerializer(many=True, read_only=True)
    # These will display the names (e.g., "Veg", "Indian") instead of just IDs
    food_types = serializers.StringRelatedField(many=True)
    cuisines = serializers.StringRelatedField(many=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'food_types', 'cuisines', 'variants']

class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        fields = ['id', 'name']

class CuisineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuisine
        fields = ['id', 'name']

class CategoryManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class RestaurantOrderListSerializer(serializers.ModelSerializer):
    """
    A detailed serializer for listing orders for the Restaurant Admin.
    """
    # We can re-use the detailed item serializer we made for the cashier
    order_items = CashierOrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            'id', 'customer_name', 'table_number', 'payment_status', 
            'payment_method', 'created_at', 'total_price', 'order_items'
        ]

    def get_total_price(self, bill):
        # Calculates the total price for the bill
        return sum(item.variant.price * item.quantity for item in bill.order_items.all())

class FrontendOrderItemSerializer(serializers.Serializer):
    """
    Validates an incoming order item from the frontend.
    """
    menu_item_id = serializers.IntegerField()
    variant_name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField(min_value=1)

class FrontendOrderSerializer(serializers.Serializer):
    """
    Validates the entire incoming order from the frontend.
    """
    table_number = serializers.CharField(max_length=50)
    customer_name = serializers.CharField(max_length=150)
    items = FrontendOrderItemSerializer(many=True)

class KitchenOrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='variant.menu_item.name', read_only=True)
    variant_name = serializers.CharField(source='variant.variant_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'variant_name', 'quantity', 'status']

class KitchenOrderSerializer(serializers.ModelSerializer):
    order_items = KitchenOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'table_number', 'customer_name', 'created_at', 'order_items']

