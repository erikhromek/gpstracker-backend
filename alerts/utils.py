from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EnablePartialUpdateMixin:
    """Enable partial updates

    Override partial kwargs in UpdateModelMixin class
    https://github.com/encode/django-rest-framework/blob/91916a4db14cd6a06aca13fb9a46fc667f6c0682/rest_framework/mixins.py#L64
    """

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


def only_int(value):
    if value.isdigit() is False:
        raise ValidationError(_("Solo se permiten números."))
