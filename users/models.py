from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        RESPONDENT = 'respondent', 'Респондент'

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.RESPONDENT,
    )

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        swappable = 'AUTH_USER_MODEL'

    @property
    def is_admin(self) -> bool:
        return (
            self.role == self.Role.ADMIN
            or self.is_superuser
            or self.is_staff
        )

    @property
    def is_respondent(self) -> bool:
        return self.role == self.Role.RESPONDENT and not self.is_admin

    def __str__(self) -> str:
        return f'{self.username} ({self.get_role_display()})'
