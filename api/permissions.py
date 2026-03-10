from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    message = 'Доступ разрешён только администраторам опросов.'

    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not (request.user and request.user.is_authenticated):
            return False
        return request.method in SAFE_METHODS or request.user.is_admin
