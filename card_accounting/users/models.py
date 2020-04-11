# -*- coding: utf-8 -*-

"""ORM models for system users."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class SysUser(AbstractUser):
    """System user class."""

    patronymic = models.CharField(_('patronymic'), max_length=100)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('last_name', 'first_name', 'patronymic', 'id')

    def __str__(self):
        """Represent user full name of sys username.

        Returns:
            Username of full name.

        """
        return self.get_full_name() or self.get_username()

    def get_full_name(self):
        """Make user full name.

        Returns:
            User full name as string.

        """
        return '{0} {1} {2}'.format(
            self.last_name,
            self.first_name,
            self.patronymic,
        )
