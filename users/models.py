from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class Organization(models.Model):
    name = models.CharField(max_length=64, null=False, blank=False)
    enabled = models.BooleanField(null=False, default=True)


class User(AbstractUser):
    ROLE = [("ADM", "Administrador"), ("OPS", "Operador")]

    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=3, choices=ROLE, blank=False)
    name = models.CharField(max_length=64, null=False, blank=False)
    surname = models.CharField(max_length=64, null=False, blank=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        verbose_name=_("organization"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
