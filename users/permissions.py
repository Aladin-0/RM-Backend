# users/permissions.py

from rest_framework.permissions import BasePermission

class IsChefOrAdmin(BasePermission):
    """
    Allows access only to users with the 'CHEF' role,
    or to authenticated Restaurant Admins.
    """
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        token_role = request.auth.get('role') if request.auth else None
        
        is_admin = user_role == 'ADMIN'
        is_chef = user_role == 'CHEF' or token_role == 'CHEF'
        
        return is_admin or is_chef

class IsCaptainOrAdmin(BasePermission):
    """
    Allows access only to users with the 'CAPTAIN' role,
    or to authenticated Restaurant Admins.
    """
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        token_role = request.auth.get('role') if request.auth else None

        is_admin = user_role == 'ADMIN'
        is_captain = user_role == 'CAPTAIN' or token_role == 'CAPTAIN'

        return is_admin or is_captain

class IsCashierOrAdmin(BasePermission):
    """
    Allows access only to users with the 'CASHIER' role,
    or to authenticated Restaurant Admins.
    """
    def has_permission(self, request, view):
        user_role = getattr(request.user, 'role', None)
        token_role = request.auth.get('role') if request.auth else None

        is_admin = user_role == 'ADMIN'
        is_cashier = user_role == 'CASHIER' or token_role == 'CASHIER'
        
        return is_admin or is_cashier
