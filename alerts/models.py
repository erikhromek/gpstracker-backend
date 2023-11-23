from django.db import models
from django.utils.translation import gettext_lazy as _

from alerts.utils import only_int
from users.models import Organization, User


class BeneficiaryType(models.Model):
    code = models.CharField(max_length=8, null=False, blank=False)
    description = models.CharField(max_length=8, null=False, blank=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("organization"),
    )


class Beneficiary(models.Model):
    COMPANY_CHOICES = [
        ("CLA", "Claro"),
        ("PER", "Personal"),
        ("MOV", "Movistar"),
        ("TUE", "Tuenti"),
        ("OTH", _("Other")),
    ]

    name = models.CharField(max_length=64, null=False, blank=False)
    surname = models.CharField(max_length=64, null=False, blank=False)
    telephone = models.CharField(
        max_length=32, null=False, blank=False, validators=[only_int]
    )
    company = models.CharField(max_length=3, choices=COMPANY_CHOICES, blank=True)
    enabled = models.BooleanField(null=False, default=True)
    description = models.CharField(max_length=512, null=False, blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("organization"),
    )
    type = models.ForeignKey(
        BeneficiaryType,
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("type"),
    )


class Alert(models.Model):
    ALERT_STATUS = [
        ("N", _("New")),
        ("A", _("Attended")),
        ("C", _("Closed")),
    ]

    datetime = models.DateTimeField(null=False)
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        null=False,
        verbose_name=_("beneficiary"),
    )

    longitude = models.DecimalField(max_digits=10, decimal_places=8)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    state = models.CharField(
        max_length=1, choices=ALERT_STATUS, null=False, default="N"
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("operator"),
    )
    observations = models.CharField(max_length=512, null=True, blank=True)
