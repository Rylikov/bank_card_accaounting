# -*- coding: utf-8 -*-

"""API module for interaction with cards."""

import json
import socket

from django.db import models
from django.http import JsonResponse
from django.utils import timezone

from cards.forms import CardCreateForm
from cards.models import Card
from snippets.views import CreateAPIView, DetailAPIView

SUCCESS_RESPONSE_CODE = 200
BAD_REQUEST_RESPONSE_CODE = 400


class CreateCardApiView(CreateAPIView):
    """New card release api class."""

    response_message = 'Card released successful'
    form_class = CardCreateForm
    return_fields = (
        ('card_number', 'created_card_number'),
        ('creation_date', 'created'),
    )

    def save_form(self):  # noqa: D102
        form = self.get_form()
        # TODO: add validation
        form.is_valid()
        self.object = Card.release_card(form.cleaned_data['card_holder'])


class CardBalanceAPIView(DetailAPIView):
    """Card balance getting api class."""

    response_message = 'Balance got successful'
    model = Card
    slug = 'card_number'
    return_fields = (('balance', '.'), )

    def get_data(self, request):  # noqa: D102
        response_data = super().get_data(request)
        response_data['time'] = timezone.now()
        return response_data


def enroll_money(request, **kwargs):
    """Enroll money on given card number.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_number = kwargs['card_number']
    transaction_info = json.loads(request.body)

    try:
        card = Card.objects.get(card_number=card_number)
    except Card.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transaction = card.update_balance(int(transaction_info['amount']))

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Money enrolled successful',
        'time': transaction.creation_date,
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


def write_off_money(request, **kwargs):
    """Write off money on given card number.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_number = kwargs['card_number']
    transaction_info = json.loads(request.body)

    try:
        card = Card.objects.get(card_number=card_number)
    except models.Model.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transaction = card.update_balance(
        int(transaction_info['amount']),
        update_type='WRITE_OFF',
    )

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Money written off successful',
        'time': transaction.creation_date,
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)


def get_transactions(request, **kwargs):
    """Get given card transactions.

    Args:
        request: HTTP request.
        kwargs: request parameters.

    Returns:
        JSON response.

    """
    card_info = kwargs

    try:
        card = Card.objects.get(card_number=card_info['card_number'])
    except models.Model.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid card number'},
            status=BAD_REQUEST_RESPONSE_CODE,
        )

    transactions = card.transaction_set.all()
    if card_info.get('list_size'):
        transactions = transactions[:card_info['list_size']]

    transactions_data = {}
    for num, transaction in enumerate(transactions):
        transactions_data[num] = {
            'type': transaction.transaction_type,
            'amount': transaction.amount,
            'date': transaction.creation_date,
        }

    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    response_data = {
        'status': 'OK',
        'message': 'Transactions got successful',
        'transactions': transactions_data,
        'time': timezone.now(),
        'server_ip': host_ip,
    }
    return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)
