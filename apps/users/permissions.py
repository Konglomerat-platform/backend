from rest_framework.permissions import BasePermission

from apps.users.models import User


def is_admin(user) -> bool:
    return bool(user and user.is_authenticated and user.role == User.Role.ADMIN)


def is_company(user) -> bool:
    return bool(user and user.is_authenticated and user.role == User.Role.COMPANY)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view) -> bool:
        return is_admin(request.user)


class IsCompanyOrAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.role in {User.Role.ADMIN, User.Role.COMPANY})
