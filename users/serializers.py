# users/serializers.py
from rest_framework import serializers
from .models import StaffUser, RoleCredential
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffUser
        fields = ['id', 'username', 'first_name', 'last_name', 'role'] 

class RoleCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleCredential
        fields = ['id', 'role', 'username', 'password']
        # Password should never be sent back in a response
        extra_kwargs = {'password': {'write_only': True}}

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = user.role
        if hasattr(user, 'restaurant') and user.restaurant:
            token['restaurant_id'] = user.restaurant.id
        return token
        
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Case 1: Check for a standard StaffUser (Restaurant Admin)
        user = authenticate(username=username, password=password)
        if user:
            refresh = self.get_token(user)
            
            return {
                'token': str(refresh.access_token),
                'user': {
                    'name': user.username,
                    'role': user.role
                }
            }

        # Case 2: Check for a shared RoleCredential (Chef, Captain, etc.)
        try:
            credential = RoleCredential.objects.get(username=username)
            if check_password(password, credential.password):
                # Manually create a token with custom data
                refresh = RefreshToken()
                refresh['user_id'] = credential.id  # Add user_id for authentication
                refresh['username'] = credential.username
                refresh['role'] = credential.role
                refresh['restaurant_id'] = credential.restaurant.id
                
                return {
                    'token': str(refresh.access_token),
                    'user': {
                        'name': credential.username,
                        'role': credential.role
                    }
                }
        except RoleCredential.DoesNotExist:
            pass # Let it fall through to the error

        raise serializers.ValidationError('No active account found with the given credentials')
