from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alerts.models import Alert, Beneficiary
from alerts.permissions import IsSameOrganization
from alerts.serializers import AlertSerializer, BeneficiarySerializer
from alerts.utils import EnablePartialUpdateMixin


class BeneficiaryViewSet(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for beneficiaries
    """

    permission_classes = (
        IsAuthenticated,
        IsSameOrganization,
    )

    serializer_class = BeneficiarySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Beneficiary.objects.filter(organization=user.organization)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.enabled = False
        instance.save()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AlertViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for beneficiaries
    """

    permission_classes = (
        IsAuthenticated,
        IsSameOrganization,
    )

    def get_queryset(self):
        user = self.request.user
        queryset = Alert.objects.filter(organization=user.organization)
        return queryset

    serializer_class = AlertSerializer
