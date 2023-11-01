from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def only_int(value):
    if value.isdigit() is False:
        raise ValidationError(_("Value must include only numbers"))
