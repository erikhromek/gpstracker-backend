# from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from alerts.models import Beneficiary
from alerts.serializers import BeneficiarySerializer

# from rest_framework.response import Response


class BeneficiaryViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for beneficiaries
    """

    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
