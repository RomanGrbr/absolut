from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    message = 'Доступ разрешён только администраторам опросов.'

    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_authenticated and request.user.is_admin
