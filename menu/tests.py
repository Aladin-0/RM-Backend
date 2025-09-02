from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from restaurants.models import Restaurant
from .models import Category, MenuItem, MenuItemVariant
from .models import Category, MenuItem, MenuItemVariant, Bill, OrderItem # Add Bill and OrderItem
from django.test import override_settings # <-- ADD THIS IMPORT


class MenuAPITests(APITestCase):
    def setUp(self):
        """
        This function runs before every single test.
        We use it to create the sample data we need.
        """
        # 1. Create a sample restaurant
        self.restaurant = Restaurant.objects.create(
            name="Test Cafe",
            slug="test-cafe",
            latitude=10.0,
            longitude=10.0
        )
        # 2. Create a sample category for that restaurant
        self.category = Category.objects.create(
            restaurant=self.restaurant,
            name="Starters"
        )
        # 3. Create a sample menu item
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            category=self.category,
            name="Paneer Tikka"
        )
        # 4. Create a sample variant for that item
        self.variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item,
            variant_name="Full Plate",
            price=250.00
        )

    def test_can_view_restaurant_menu(self):
        """
        This is our actual test. It checks if an anonymous user
        can successfully view the menu for a specific restaurant.
        """
        # Get the correct URL for our test restaurant's menu
        url = reverse('customer-menu-list', kwargs={'restaurant_slug': self.restaurant.slug})

        # Simulate a GET request to that URL
        response = self.client.get(url)

        # --- Assertions ---
        # We check if the server responded with a 200 OK status.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We check if the response body contains the names of the items we created.
        self.assertContains(response, "Starters")
        self.assertContains(response, "Paneer Tikka")
        self.assertContains(response, "Full Plate")


class MenuAPITests(APITestCase):
    # ... (your existing, working test class is here - no changes needed)
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Test Cafe", slug="test-cafe", latitude=10.0, longitude=10.0
        )
        self.category = Category.objects.create(
            restaurant=self.restaurant, name="Starters"
        )
        self.menu_item = MenuItem.objects.create(
            restaurant=self.restaurant, category=self.category, name="Paneer Tikka"
        )
        self.variant = MenuItemVariant.objects.create(
            menu_item=self.menu_item, variant_name="Full Plate", price=250.00
        )

    def test_can_view_restaurant_menu(self):
        url = reverse('customer-menu-list', kwargs={'restaurant_slug': self.restaurant.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Paneer Tikka")


@override_settings(CHANNEL_LAYERS={
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
})
class OrderAPITests(APITestCase):
    def setUp(self):
        """Set up a restaurant with a specific location for geofence testing."""
        self.restaurant = Restaurant.objects.create(
            name="Live Test Diner",
            slug="live-test-diner",
            latitude=12.9716, # Bangalore coordinates
            longitude=77.5946,
            radius_meters=200
        )
        category = Category.objects.create(restaurant=self.restaurant, name="Main Course")
        menu_item = MenuItem.objects.create(
            restaurant=self.restaurant, category=category, name="Pizza"
        )
        self.variant = MenuItemVariant.objects.create(
            menu_item=menu_item, variant_name="12 inch", price=500.00
        )

    def test_create_order_success_inside_geofence(self):
        """
        Ensure a customer can place an order when they are inside the geofence.
        """
        url = reverse('customer-order-create', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            "customer_name": "Test Customer",
            "table_number": "5",
            "location": "12.9715,77.5945",  # Location NEAR the restaurant
            "order_items": [
                {"variant_id": self.variant.id, "quantity": 1}
            ]
        }
        
        response = self.client.post(url, data, format='json')

        # Assert that the order was created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Assert that one Bill object now exists in the test database
        self.assertEqual(Bill.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(Bill.objects.first().customer_name, "Test Customer")

    def test_create_order_fail_outside_geofence(self):
        """
        Ensure a customer is blocked from ordering when they are outside the geofence.
        """
        url = reverse('customer-order-create', kwargs={'restaurant_slug': self.restaurant.slug})
        data = {
            "customer_name": "Far Away Customer",
            "table_number": "5",
            "location": "13.0827,80.2707",  # Location FAR from the restaurant (Chennai)
            "order_items": [
                {"variant_id": self.variant.id, "quantity": 1}
            ]
        }
        
        response = self.client.post(url, data, format='json')

        # Assert that the request was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Assert that NO Bill was created in the database
        self.assertEqual(Bill.objects.count(), 0)