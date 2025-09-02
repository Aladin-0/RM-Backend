# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserInfoView, RoleCredentialViewSet

# Create a router for the management endpoints
router = DefaultRouter()
router.register(r'staff-credentials', RoleCredentialViewSet, basename='staff-credential')

urlpatterns = [
    path('user/', UserInfoView.as_view(), name='user-info'),
    # Add the router's URLs to the list
    path('', include(router.urls)),
]