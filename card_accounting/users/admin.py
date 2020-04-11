# -*- coding: utf-8 -*-

"""Admin site register models module."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import SysUser


class SysUserAdmin(UserAdmin):
    """System user admin class."""

    search_fields = ('username', 'first_name', 'last_name', 'patronymic')

    fieldsets = UserAdmin.fieldsets
    old_fieldsets = fieldsets[1][1]['fields']
    new_fieldsets = old_fieldsets[:2] + ('patronymic', ) + old_fieldsets[2:]
    fieldsets[1][1]['fields'] = new_fieldsets

    add_fieldsets = UserAdmin.add_fieldsets
    old_add_fieldsets = add_fieldsets[0][1]['fields']
    extra_fields = ('first_name', 'last_name', 'patronymic')
    new_add_fieldsets = extra_fields + old_add_fieldsets
    add_fieldsets[0][1]['fields'] = new_add_fieldsets


admin.site.register(SysUser, SysUserAdmin)
