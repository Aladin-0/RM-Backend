# menu/views.py
from django.shortcuts import render,get_object_or_404
from rest_framework import generics, viewsets 
from .models import Category , OrderItem ,Bill ,MenuItem , MenuItemVariant
from .serializers import CategorySerializer, BillSerializer, OrderItemWriteSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from geopy.distance import geodesic
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from users.permissions import IsChefOrAdmin, IsCaptainOrAdmin, IsCashierOrAdmin
from restaurants.models import Restaurant 
from .models import FoodType, Cuisine, Category 
from .serializers import FoodTypeSerializer, CuisineSerializer, CategoryManageSerializer 
from .serializers import RestaurantOrderListSerializer, KitchenOrderSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from .serializers import CashierBillSerializer ,MenuItemManageSerializer , PublicMenuItemSerializer, PublicMenuItemVariantSerializer
from django.utils import timezone
from django.db.models import Sum, F, Count
from .serializers import FrontendOrderSerializer
from datetime import timedelta


# class MenuListView(generics.ListAPIView):
#     serializer_class = CategorySerializer

#     def get_queryset(self):
#         """
#         This view now returns the menu for a specific restaurant,
#         identified by the 'slug' in the URL.
#         """
#         restaurant_slug = self.kwargs.get('restaurant_slug')
#         restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
#         return Category.objects.filter(restaurant=restaurant).prefetch_related('menu_items__variants')

class OrderCreateView(APIView):
   

    def post(self, request, restaurant_slug, *args, **kwargs):
        # First, get the specific restaurant from the URL
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        
        # --- DYNAMIC Geofencing Logic ---
        customer_location_str = request.data.get('location')
        if not customer_location_str:
            return Response({'error': 'Location is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lat, lon = map(float, customer_location_str.split(','))
            customer_location = (lat, lon)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid location format.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the restaurant's location from the database
        restaurant_location = (restaurant.latitude, restaurant.longitude)
        max_distance = restaurant.radius_meters

        distance = geodesic(restaurant_location, customer_location).meters
        if distance > max_distance:
            return Response({'error': 'You are too far away to place an order.'}, status=status.HTTP_403_FORBIDDEN)
            
        # Process the order
        serializer = BillSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Assign the bill to the correct restaurant before saving
        bill_instance = serializer.save(restaurant=restaurant)

        # ... (The rest of the WebSocket logic remains the same) ...
        detailed_items = [{
            'order_item_id': item.id, 'name': item.variant.menu_item.name,
            'variant': item.variant.variant_name, 'quantity': item.quantity
        } for item in bill_instance.order_items.all()]
        
        websocket_message = {
            'bill_id': bill_instance.id, 'customer_name': bill_instance.customer_name,
            'table_number': bill_instance.table_number, 'items': detailed_items
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chef_notifications_{restaurant.slug}', # Channel is now restaurant-specific
            {'type': 'send.new.order', 'data': websocket_message}
        )
        
        response_data = {
            'bill_id': bill_instance.id, 'customer_name': bill_instance.customer_name,
            'table_number': bill_instance.table_number, 'order_items': detailed_items
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class ChefOrderItemUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsChefOrAdmin]

    def post(self, request, *args, **kwargs):
        order_item_id = kwargs.get("item_id")
        new_status = request.data.get("status")

        valid_statuses = [choice[0] for choice in OrderItem.OrderStatus.choices]
        if new_status not in valid_statuses:
            return Response({"error": "Invalid status provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_item = OrderItem.objects.get(id=order_item_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        order_item.status = new_status
        order_item.save()

        customer_message = {
            'order_item_id': order_item.id,
            'new_status': order_item.get_status_display()
        }

        if new_status == OrderItem.OrderStatus.ACCEPTED:
            customer_message['preparation_time'] = order_item.variant.preparation_time

        try:
            channel_layer = get_channel_layer()
            customer_bill_id = order_item.bill.id

            async_to_sync(channel_layer.group_send)(
                f'customer_{customer_bill_id}',
                {
                    'type': 'send_status_update',
                    'data': customer_message
                }
            )
        except Exception as e:
            # Log the error but continue with the response
            print(f"WebSocket notification error: {e}")
            # The status update was still saved to the database

        return Response({"message": f"Order item {order_item_id} updated to {new_status}"}, status=status.HTTP_200_OK)

class CaptainOrderCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCaptainOrAdmin]

    def post(self, request, *args, **kwargs):
        serializer = BillSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get the restaurant from the user
        restaurant = request.user.restaurant
        if not restaurant:
            return Response(
                {"error": "User is not associated with any restaurant"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bill_instance = serializer.save(restaurant=restaurant)

        # Build and send the WebSocket message
        detailed_items = [{
            'order_item_id': item.id, 'name': item.variant.menu_item.name,
            'variant': item.variant.variant_name, 'quantity': item.quantity
        } for item in bill_instance.order_items.all()]
        
        websocket_message = {
            'bill_id': bill_instance.id, 'customer_name': bill_instance.customer_name,
            'table_number': bill_instance.table_number, 'items': detailed_items
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chef_notifications_{restaurant.slug}',
            {'type': 'send.new.order', 'data': websocket_message}
        )
        
        response_data = {
            'bill_id': bill_instance.id, 'customer_name': bill_instance.customer_name,
            'table_number': bill_instance.table_number, 'order_items': detailed_items
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class CaptainReorderView(APIView):
    permission_classes = [IsAuthenticated, IsCaptainOrAdmin]

    def post(self, request, bill_id, *args, **kwargs):
        try:
            bill = Bill.objects.get(id=bill_id, payment_status=Bill.PaymentStatus.PENDING)
        except Bill.DoesNotExist:
            return Response({"error": "Active bill not found."}, status=status.HTTP_404_NOT_FOUND)

        # We need a serializer to validate the incoming item data
        # We can reuse the OrderItemSerializer for this
        item_serializer = OrderItemWriteSerializer(data=request.data.get('order_items', []), many=True)
        if not item_serializer.is_valid():
            return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_items_data = item_serializer.validated_data
        new_order_items = []
        for item_data in new_items_data:
            order_item = OrderItem.objects.create(
                bill=bill,
                variant_id=item_data['variant_id'],
                quantity=item_data['quantity']
            )
            new_order_items.append(order_item)

        # --- Broadcast ONLY the new items to the Chef Panel ---
        detailed_items = []
        for item in new_order_items:
            detailed_items.append({
                'order_item_id': item.id, 'name': item.variant.menu_item.name,
                'variant': item.variant.variant_name, 'quantity': item.quantity
            })
        
        websocket_message = {
            'bill_id': bill.id, 'customer_name': bill.customer_name,
            'table_number': bill.table_number, 'items': detailed_items
        }
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chef_notifications',
            {'type': 'send.new.order', 'data': websocket_message}
        )

        return Response({"message": "Items added successfully."}, status=status.HTTP_200_OK)

class CashierBillListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]
    serializer_class = CashierBillSerializer
    queryset = Bill.objects.filter(payment_status=Bill.PaymentStatus.PENDING).prefetch_related('order_items__variant__menu_item')

class CashierMarkAsPaidView(APIView):
    permission_classes = [IsAuthenticated, IsCashierOrAdmin]

    def post(self, request, bill_id, *args, **kwargs):
        try:
            bill = Bill.objects.get(id=bill_id, payment_status=Bill.PaymentStatus.PENDING)
        except Bill.DoesNotExist:
            return Response({"error": "Active bill not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the payment method from the request body
        payment_method = request.data.get('payment_method')

        # Validate the input to ensure it's either 'ONLINE' or 'OFFLINE'
        valid_methods = [choice[0] for choice in Bill.PaymentMethod.choices]
        if payment_method not in valid_methods:
            return Response(
                {'error': f"Invalid payment_method. Must be one of {valid_methods}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update the bill with both the new status and the payment method
        bill.payment_status = Bill.PaymentStatus.PAID
        bill.payment_method = payment_method
        bill.save()
        
        return Response({"message": f"Bill {bill_id} has been marked as PAID with method {payment_method}."}, status=status.HTTP_200_OK)

class AdminAnalyticsView(APIView):
    """
    Provides analytics data for the admin dashboard.
    """


    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # --- 1. Calculate Sales Today ---
        sales_today_query = OrderItem.objects.filter(
            bill__payment_status=Bill.PaymentStatus.PAID,
            created_at__date=today
        ).aggregate(
            total_sales=Sum(F('quantity') * F('variant__price'))
        )
        sales_today = sales_today_query['total_sales'] or 0

        # --- 2. Calculate Sales This Month ---
        sales_month_query = OrderItem.objects.filter(
            bill__payment_status=Bill.PaymentStatus.PAID,
            created_at__year=current_year,
            created_at__month=current_month
        ).aggregate(
            total_sales=Sum(F('quantity') * F('variant__price'))
        )
        sales_this_month = sales_month_query['total_sales'] or 0

        # --- 3. Find Top Dish Today ---
        top_dish_today_query = OrderItem.objects.filter(
            bill__payment_status=Bill.PaymentStatus.PAID,
            created_at__date=today
        ).values(
            'variant__menu_item__name', 'variant__variant_name'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity').first()
        
        top_dish_today = "N/A"
        if top_dish_today_query:
            top_dish_today = f"{top_dish_today_query['variant__menu_item__name']} ({top_dish_today_query['variant__variant_name']})"

        # --- 4. Find Top Dish This Month ---
        top_dish_month_query = OrderItem.objects.filter(
            bill__payment_status=Bill.PaymentStatus.PAID,
            created_at__year=current_year,
            created_at__month=current_month
        ).values(
            'variant__menu_item__name', 'variant__variant_name'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity').first()

        top_dish_this_month = "N/A"
        if top_dish_month_query:
            top_dish_this_month = f"{top_dish_month_query['variant__menu_item__name']} ({top_dish_month_query['variant__variant_name']})"

        # --- Assemble the final data ---
        data = {
            'sales_today': f"{sales_today:.2f}",
            'sales_this_month': f"{sales_this_month:.2f}",
            'top_dish_today': top_dish_today,
            'top_dish_this_month': top_dish_this_month
        }

        return Response(data, status=status.HTTP_200_OK)

class MenuItemManageViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for Restaurant Admins to manage their own MenuItems.
    """
    serializer_class = MenuItemManageSerializer
    permission_classes = [IsAuthenticated] # Ensures only logged-in users can access this

    def get_queryset(self):
        """
        This is the key to multi-tenancy. It filters the menu items to show
        only the ones that belong to the logged-in user's restaurant.
        """
        user = self.request.user
        return MenuItem.objects.filter(restaurant=user.restaurant)

    def perform_create(self, serializer):
        """
        This is another key to multi-tenancy. When a new menu item is created,
        it's automatically assigned to the logged-in user's restaurant.
        """
        serializer.save(restaurant=self.request.user.restaurant)

class PublicMenuListView(generics.ListAPIView):
    """
    Provides a public, flat list of all available menu items for a
    specific restaurant.
    """
    serializer_class = PublicMenuItemSerializer
    permission_classes = [AllowAny] # This is a public endpoint

    def get_queryset(self):
        """
        Filters the menu to show only available items for the restaurant
        specified in the URL.
        """
        restaurant_slug = self.kwargs.get('restaurant_slug')
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)
        
        # Return only items that are marked as available for that restaurant
        return MenuItem.objects.filter(
            restaurant=restaurant,
            is_available=True
        ).prefetch_related('variants', 'food_types', 'cuisines')

class CategoryManageViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryManageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)

class FoodTypeViewSet(viewsets.ModelViewSet):
    serializer_class = FoodTypeSerializer
    permission_classes = [IsAuthenticated]
    queryset = FoodType.objects.all() # These are global, not per-restaurant

class CuisineViewSet(viewsets.ModelViewSet):
    serializer_class = CuisineSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cuisine.objects.all() # These are also global

class RestaurantOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only API endpoint for a Restaurant Admin to view
    their own restaurant's orders.
    """
    serializer_class = RestaurantOrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This is the key to security and multi-tenancy.
        It filters orders to only those belonging to the logged-in user's restaurant
        and shows the most recent ones first.
        """
        return Bill.objects.filter(
            restaurant=self.request.user.restaurant
        ).order_by('-created_at').prefetch_related('order_items__variant__menu_item')

class RestaurantAnalyticsView(APIView):
    """
    Provides analytics data specifically for the logged-in Restaurant Admin.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        current_month = today.month
        current_year = today.year

        # Base queryset filtered for the admin's restaurant and paid bills
        base_queryset = OrderItem.objects.filter(
            bill__restaurant=user.restaurant,
            bill__payment_status=Bill.PaymentStatus.PAID
        )

        # 1. Calculate Sales Today
        sales_today_query = base_queryset.filter(created_at__date=today).aggregate(
            total_sales=Sum(F('quantity') * F('variant__price'))
        )
        sales_today = sales_today_query['total_sales'] or 0

        # 2. Calculate Sales This Month
        sales_month_query = base_queryset.filter(
            created_at__year=current_year, created_at__month=current_month
        ).aggregate(
            total_sales=Sum(F('quantity') * F('variant__price'))
        )
        sales_this_month = sales_month_query['total_sales'] or 0

        # 3. Find Top Dish Today
        top_dish_today_query = base_queryset.filter(created_at__date=today).values(
            'variant__menu_item__name', 'variant__variant_name'
        ).annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').first()
        
        top_dish_today = "N/A"
        if top_dish_today_query:
            top_dish_today = f"{top_dish_today_query['variant__menu_item__name']} ({top_dish_today_query['variant__variant_name']})"

        # 4. Find Top Dish This Month
        top_dish_month_query = base_queryset.filter(
            created_at__year=current_year, created_at__month=current_month
        ).values(
            'variant__menu_item__name', 'variant__variant_name'
        ).annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').first()

        top_dish_this_month = "N/A"
        if top_dish_month_query:
            top_dish_this_month = f"{top_dish_month_query['variant__menu_item__name']} ({top_dish_month_query['variant__variant_name']})"

        # Assemble the final data
        data = {
            'sales_today': f"{sales_today:.2f}",
            'sales_this_month': f"{sales_this_month:.2f}",
            'top_dish_today': top_dish_today,
            'top_dish_this_month': top_dish_this_month
        }

        return Response(data, status=status.HTTP_200_OK)

class FrontendOrderCreateView(APIView):
    """
    Handles order creation based on the frontend team's spec.
    """
    permission_classes = [AllowAny] # This is a public endpoint

    def post(self, request, restaurant_slug, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)

        # 1. Validate the incoming data format
        serializer = FrontendOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data

        # 2. Create the Bill
        bill = Bill.objects.create(
            restaurant=restaurant,
            customer_name=validated_data['customer_name'],
            table_number=validated_data['table_number']
        )
        
        # 3. Find variants and create OrderItems
        order_items_for_broadcast = []
        try:
            for item_data in validated_data['items']:
                variant = MenuItemVariant.objects.get(
                    menu_item_id=item_data['menu_item_id'],
                    variant_name=item_data['variant_name'],
                    menu_item__restaurant=restaurant # Ensure it belongs to this restaurant
                )
                order_item = OrderItem.objects.create(
                    bill=bill,
                    variant=variant,
                    quantity=item_data['quantity']
                )
                # Prepare item details for the real-time message
                order_items_for_broadcast.append({
                    'order_item_id': order_item.id, 'name': variant.menu_item.name,
                    'variant': variant.variant_name, 'quantity': order_item.quantity
                })
        except MenuItemVariant.DoesNotExist:
            # If any item is invalid, delete the created bill and return an error
            bill.delete()
            return Response({'error': 'An invalid menu item was submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Broadcast to the Chef's Panel
        websocket_message = {
            'bill_id': bill.id, 'customer_name': bill.customer_name,
            'table_number': bill.table_number, 'items': order_items_for_broadcast
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chef_notifications_{restaurant.slug}',
            {'type': 'send.new.order', 'data': websocket_message}
        )
        
        # 5. Return the response in the format the frontend expects
        response_data = {
            "order_id": bill.id,
            "queue_number": bill.id # Using the bill ID as a simple queue number
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class KitchenOrderListView(generics.ListAPIView):
    """
    Provides a list of all active (pending or accepted) orders
    for the logged-in Chef or Restaurant Admin.
    """
    serializer_class = KitchenOrderSerializer
    permission_classes = [IsAuthenticated, IsChefOrAdmin]

    def get_queryset(self):
        user = self.request.user
        
        # Determine the restaurant from the logged-in user (Admin) or token (Chef)
        if hasattr(user, 'restaurant') and user.restaurant:
            restaurant = user.restaurant
        else:
            restaurant_id = self.request.auth.get('restaurant_id')
            restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Fetch unpaid bills that have at least one item that is not yet completed
        return Bill.objects.filter(
            restaurant=restaurant,
            payment_status=Bill.PaymentStatus.PENDING,
            order_items__status__in=[
                OrderItem.OrderStatus.PENDING,
                OrderItem.OrderStatus.ACCEPTED
            ]
        ).distinct().order_by('created_at').prefetch_related('order_items__variant__menu_item')

class AdminOrderReportView(generics.ListAPIView):
    """
    Provides a historical order report for the Restaurant Admin,
    filterable by a time period ('today', 'week', 'month', 'year').
    """
    serializer_class = RestaurantOrderListSerializer # We can reuse our detailed order serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        restaurant = user.restaurant
        
        # Get the 'period' from the URL, e.g., /.../?period=week
        period = self.request.query_params.get('period', 'today').lower()
        
        today = timezone.now().date()
        queryset = Bill.objects.filter(restaurant=restaurant)

        if period == 'today':
            queryset = queryset.filter(created_at__date=today)
        elif period == 'week':
            start_of_week = today - timedelta(days=7)
            queryset = queryset.filter(created_at__date__gte=start_of_week)
        elif period == 'month':
            queryset = queryset.filter(created_at__year=today.year, created_at__month=today.month)
        elif period == 'year':
            queryset = queryset.filter(created_at__year=today.year)
        
        return queryset.order_by('-created_at')
