# -*- coding: utf-8 -*-

"""ORM models for bank cards operations."""

from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from cards.signals import create_operation


class CardHolder(models.Model):
    """Class, that handle information about card holder."""

    first_name = models.CharField(_('first name'), max_length=50)  # noqa:WPS432
    last_name = models.CharField(_('last name'), max_length=100)
    patronymic = models.CharField(_('patronymic'), max_length=100)
    phone_number = models.PositiveIntegerField(_('phone number'))
    creation_date = models.DateTimeField(_('creation date'), auto_now=True)

    class Meta:
        verbose_name = _('card holder')
        verbose_name_plural = _('card holders')


class Card(models.Model):
    """Class that handle information about card."""

    card_number = models.BigIntegerField(
        _('card number'),
        unique=True,
        editable=False,
    )
    balance = models.BigIntegerField(
        _('balance'),
        default=0,
    )
    card_holder = models.ForeignKey(
        CardHolder,
        on_delete=models.CASCADE,
        verbose_name=_('card holder name'),
    )
    creation_date = models.DateTimeField(_('creation date'), auto_now=True)

    class Meta:
        verbose_name = _('card')
        verbose_name_plural = _('cards')

    @classmethod
    def release_card(cls, holder):
        """Create new card for holder.

        Args:
            holder: holder, who would owns a new card.

        Returns:
            New card object.

        """
        last_released_card = cls.objects.last()
        if last_released_card is not None:
            return cls.objects.create(
                card_number=last_released_card.card_number + 1,
                card_holder=holder,
            )

        start_card_number = 5000400030002000
        return cls.objects.create(
            card_number=start_card_number,
            card_holder=holder,
        )

    def create_operation(self, operation_type):
        """Create card operation.

        Args:
            operation_type: type of creating operation. Could be "CREATE" or
                "DELETE".

        Returns:
            Created operation.

        """
        return Operation.objects.create(
            card=self,
            operation_type=operation_type,
        )

    def update_balance(self, amount, update_type='ENROLLMENT'):
        """Update card balance.

        Args:
            amount: amount, that should be added or written off from card.
            update_type: type of update. Could be "ENROLLMENT" or "WRITE_OFF".

        Returns:
            Created transaction.

        """
        return Transaction.objects.create(
            card=self,
            amount=amount,
            transaction_type=update_type,
        )


post_save.connect(create_operation, sender=Card)


class Transaction(models.Model):
    """Card transaction class."""

    transaction_types = (
        ('ENROLLMENT', _('enrollment')),
        # TODO: add transaction bill mailing
        ('WRITE_OFF', _('write off')),
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        verbose_name=_('card'),
    )
    transaction_type = models.CharField(
        _('transaction type'),
        choices=transaction_types,
        max_length=12,  # noqa: WPS432
    )
    amount = models.BigIntegerField(_('amount'))
    creation_date = models.DateTimeField(_('creation date'), auto_now=True)

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    @transaction.atomic
    def save(self, *args, **kwargs):  # noqa: D102
        if self.transaction_type == 'ENROLLMENT':
            self.card.balance += self.amount
        elif self.transaction_type == 'WRITE_OFF':
            self.card.balance -= self.amount
        self.card.save()
        return super().save(*args, **kwargs)


class Operation(models.Model):
    """Card operation class."""

    operation_types = (
        ('CREATE', _('create')),
        ('DELETE', _('delete')),
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        verbose_name=_('card'),
    )
    operation_type = models.CharField(
        _('operation type'),
        choices=operation_types,
        max_length=6,
    )
    creation_date = models.DateTimeField(_('creation date'), auto_now=True)

    class Meta:
        verbose_name = _('operation')
        verbose_name_plural = _('operations')
