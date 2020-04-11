# -*- coding: utf-8 -*-

"""Signals handlers module."""


def create_operation(sender, instance, **kwargs):
    """Create operation on card creation.

    Args:
        sender: sender class.
        instance: sender object.
        kwargs: kwargs.
    """
    if kwargs['created']:
        instance.create_operation(operation_type='CREATE')
