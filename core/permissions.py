from rest_framework import permissions
from .models import User

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Roles.ADMIN)

class IsProjectMemberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Roles.ADMIN:
            return True
        return request.user in obj.members.all()

class IsTaskAssignedOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Roles.ADMIN:
            return True
        if request.method in permissions.SAFE_METHODS:
            return request.user == obj.assigned_to
        return request.user == obj.assigned_to
