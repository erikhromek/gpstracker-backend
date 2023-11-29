from rest_framework import permissions


class IsSameOrganization(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.organization == request.user.organization:
            return True
        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ADM"
