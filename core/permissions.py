from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', None) in ('super_admin', 'system_admin')
        )


class HasRolePermission(BasePermission):
    required_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user_role = getattr(request.user, 'role', None)
        if request.user.is_superuser:
            return True
        if self.required_roles:
            return user_role in self.required_roles
        return True


class IsBranchScoped(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if getattr(request.user, 'role', None) in ('super_admin', 'system_admin'):
            return True
        user_branch = getattr(request.user, 'branch', None)
        if not user_branch:
            return False
        obj_branch = getattr(obj, 'branch', None)
        return obj_branch == user_branch


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if getattr(request.user, 'role', None) in ('super_admin', 'system_admin'):
            return True
        owner = getattr(obj, 'user', None) or getattr(obj, 'created_by', None)
        return owner == request.user


class IsCustomerOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if getattr(request.user, 'role', None) in ('super_admin', 'system_admin'):
            return True
        customer = getattr(obj, 'customer', None)
        if customer and hasattr(customer, 'user'):
            return customer.user == request.user
        return getattr(obj, 'user', None) == request.user


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')

    def has_object_permission(self, request, view, obj):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
