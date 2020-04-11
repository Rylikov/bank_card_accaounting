# -*- coding: utf-8 -*-

"""Class based api views."""

import json
import socket

from django.db.models.functions import Lower
from django.http import JsonResponse
from django.views.generic.edit import ModelFormMixin

SUCCESS_RESPONSE_CODE = 200

METHOD_NOT_ALLOWED_RESPONSE_CODE = 405


class BaseAPIView:
    """API base view class."""

    allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
    response_message = 'Everything OK.'

    def __init__(self, request, *args, **kwargs):
        """Make class instance.

        Args:
            request: given request from handler.
            args: args.
            kwargs: kwargs.

        """
        super().__init__()
        self.request = request

    @classmethod
    def as_view(cls):
        """Make class into callable view.

        Returns:
            View function.

        """
        def view(request, *args, **kwargs):
            inited_cls = cls(request, *args, **kwargs)
            return cls.validate_request(inited_cls, request, *args, **kwargs)
        return view

    def validate_request(self, request, *args, **kwargs):
        """Validate given request.

        Args:
            request: given request.
            args: args.
            kwargs: kwargs.

        Returns:
            Error response if request is invalid, calls render function if
            request is valid.
        """
        if request.method not in self.allowed_methods:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            return JsonResponse(
                {'status': 'ERROR',
                 'message': 'Method not allowed',
                 'server_ip': host_ip,
                 },
                status=METHOD_NOT_ALLOWED_RESPONSE_CODE,
            )

        if request.method == 'PUT':  # TODO: refactor
            request.PUT = json.loads(request.body)

        if request.method == 'DELETE':  # TODO: refactor
            request.DELETE = json.loads(request.body)

        return self.render_to_response(request, *args, **kwargs)

    def render_to_response(self, request, *args, **kwargs):
        """Render given data.

        Args:
            request: given request.
            args: args.
            kwargs: kwargs.

        Returns:
            Json response.

        """
        response_data = self.get_data(request)
        return JsonResponse(response_data, status=SUCCESS_RESPONSE_CODE)

    def get_data(self, request):
        """Make data for response.

        Args:
            request: given request.

        Returns:
            Formatted data in dict.

        """
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return {
            'status': 'OK',
            'message': self.response_message,
            'server_ip': host_ip,
        }


class CreateAPIView(ModelFormMixin, BaseAPIView):
    """Class view, that create new object."""

    allowed_methods = ['POST']

    return_fields = '__all__'
    object = None  # noqa: A003

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save_form()

    def get_data(self, request):
        response_data = super().get_data(request)
        if self.return_fields == '__all__':
            for key, value in self.object.__dict__.items():
                response_data[key] = value
        else:
            for object_key, response_key in self.return_fields:
                if response_key == '.':
                    response_key = object_key
                response_data[response_key] = getattr(self.object, object_key)
        return response_data

    def save_form(self):
        """Save form into class object."""
        form = self.get_form()  # TODO: add validation
        self.object = form.save()


class DetailAPIView(BaseAPIView):
    """Class view, that give information about single object."""

    allowed_methods = ['GET']

    model = None
    queryset = None
    slug = None
    return_fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = self.get_object(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        """Get object of a given model by slug.

        Args:
            args: args.
            kwargs: kwargs.

        Returns:
            Model object.

        """
        if self.slug is None:
            self.slug = 'pk'
        search_parameter = {self.slug: kwargs[self.slug]}

        if self.model is not None:
            self.queryset = self.model.objects.all()
        return self.queryset.get(**search_parameter)

    def get_data(self, request):
        data = super().get_data(request)
        if self.return_fields == '__all__':
            for key, value in self.object.__dict__.items():  # TODO: watch later
                data[key] = value
        else:
            for object_key, response_key in self.return_fields:
                if response_key == '.':
                    response_key = object_key
                data[response_key] = getattr(self.object, object_key)
        return data


class ListAPIView(BaseAPIView):
    """Class view, that give information about multiple objects."""

    allowed_methods = ['GET']

    model = None
    queryset = None
    model_return_fields = '__all__'
    query_return_name = 'items'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.queryset is None:
            self.queryset = self.get_queryset()
        if self.model_return_fields != '__all__':
            self.model_return_fields = self.get_return_fields()

    def get_return_fields(self):
        """Parse fields, that should be returned.

        Returns:
            Parsed fields as a dict.

        """
        result_dict = {'fields': [], 'expressions': []}
        for fields in self.model_return_fields:
            if type(fields) is not str:  # noqa: WPS516
                result_dict['expressions'].append(fields)
                continue

            result_dict['fields'].append(fields)
        return result_dict

    def get_queryset(self):
        """Get queryset.

        Returns:
            Instances queryset.

        """
        return self.model.objects.all()

    def get_data(self, request):
        data = super().get_data(request)
        data[self.query_return_name] = self.serialize_query()
        return data

    def serialize_query(self):
        """Serialize query to dict format with specified fields.

        Returns:
            List of serialized instances.

        """
        if self.model_return_fields != '__all__':
            expressions = {
                response_key: Lower(object_key) for object_key, response_key
                in self.model_return_fields['expressions']
            }
            return list(self.queryset.values(
                *self.model_return_fields['fields'],
                **expressions,
            ))

        return list(self.queryset.values())
