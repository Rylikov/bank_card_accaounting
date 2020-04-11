# -*- coding: utf-8 -*-

"""Cards forms classes."""

from django import forms

from cards.models import Card


class CardCreateForm(forms.ModelForm):
    """Card creation class."""

    class Meta:
        model = Card
        fields = ['card_holder']
