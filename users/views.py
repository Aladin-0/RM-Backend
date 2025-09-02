# users/views.py
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

from rest_framework import viewsets
from .models import RoleCredential
from .serializers import RoleCredentialSerializer

class UserInfoView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class RoleCredentialViewSet(viewsets.ModelViewSet):
    """
    Allows Restaurant Admins to manage shared credentials for their staff.
    """
    serializer_class = RoleCredentialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show credentials for the admin's own restaurant
        return RoleCredential.objects.filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        # Automatically assign the credential to the admin's restaurant
        serializer.save(restaurant=self.request.user.restaurant)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
