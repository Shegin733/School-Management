

from rest_framework import  status
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user.role == 'admin' :
                return True
        return False
class IsAdminOrOfficeStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user and request.user.role in ['admin', 'staff']:
                return True
            if request.method in permissions.SAFE_METHODS:
                return True
            return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

class IsLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user and request.user.groups.filter(name='Librarian').exists():
                return request.method in ['GET', 'PATCH', 'PUT']
            return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            if obj.status == 'returned' and request.method in ['PATCH', 'PUT']:
                return False
            return True

class IsAdminOrStaffOrLibrarian(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user and request.user.role in ['admin', 'staff', 'librarian']:
                return True
            return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

class IsOfficeStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.user and request.user.role == 'staff':
                return True
            return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)

class IsOfficeStaffLibrary(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                if request.user and request.user.role == 'staff':
                    return True
                return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)
            return Response({'message': "You don't have permission to access this."}, status=status.HTTP_403_FORBIDDEN)
