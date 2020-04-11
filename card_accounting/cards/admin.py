# -*- coding: utf-8 -*-

"""Admin site register models module."""

from django.contrib import admin

from cards.models import CardHolder

admin.site.register(CardHolder)
