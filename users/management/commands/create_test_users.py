from django.core.management.base import BaseCommand
from users.models import StaffUser, RoleCredential
from restaurants.models import Restaurant
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates test users for API testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test users...')
        
        with transaction.atomic():
            # Check if test restaurant exists
            restaurant, created = Restaurant.objects.get_or_create(
                name="Test Restaurant",
                defaults={
                    "address": "123 Test Street",
                    "slug": "test-restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "radius_meters": 100
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created test restaurant: {restaurant.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Using existing restaurant: {restaurant.name}"))
            
            # Create admin user
            admin_user, created = StaffUser.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@example.com",
                    "is_staff": True,
                    "is_superuser": True,
                    "role": "ADMIN",
                    "restaurant": restaurant
                }
            )
            
            if created:
                admin_user.set_password("admin123")
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"Using existing admin user: {admin_user.username}"))
            
            # Create staff users
            staff_roles = [
                {"username": "chef", "password": "chef123", "role": "CHEF"},
                {"username": "cashier", "password": "cashier123", "role": "CASHIER"},
                {"username": "captain", "password": "captain123", "role": "CAPTAIN"}
            ]
            
            for staff_data in staff_roles:
                staff_user, created = StaffUser.objects.get_or_create(
                    username=staff_data["username"],
                    defaults={
                        "email": f"{staff_data['username']}@example.com",
                        "role": staff_data["role"],
                        "restaurant": restaurant
                    }
                )
                
                if created:
                    staff_user.set_password(staff_data["password"])
                    staff_user.save()
                    self.stdout.write(self.style.SUCCESS(f"Created staff user: {staff_user.username}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Using existing staff user: {staff_user.username}"))
                
                # Create or update RoleCredential
                role_credential, created = RoleCredential.objects.get_or_create(
                    restaurant=restaurant,
                    role=staff_data["role"],
                    defaults={
                        "username": staff_data["username"],
                        "password": staff_data["password"]
                    }
                )
                
                if not created:
                    # Update the password if needed
                    role_credential.username = staff_data["username"]
                    role_credential.password = staff_data["password"]
                    role_credential.save()
            
            self.stdout.write(self.style.SUCCESS('\nTest data setup complete!'))
            self.stdout.write('You can now run the API tests with the following credentials:')
            self.stdout.write('Admin: username=admin, password=admin123')
            self.stdout.write('Chef: username=chef, password=chef123')
            self.stdout.write('Cashier: username=cashier, password=cashier123')
            self.stdout.write('Captain: username=captain, password=captain123')