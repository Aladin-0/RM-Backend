# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StaffUser

class StaffUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'restaurant', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Restaurant Info', {'fields': ('role', 'restaurant')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # If the user is a superuser, show all users
        if request.user.is_superuser:
            return qs
        # Otherwise, filter to only show users from their own restaurant
        return qs.filter(restaurant=request.user.restaurant)

admin.site.register(StaffUser, StaffUserAdmin)
