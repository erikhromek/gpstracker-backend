from datetime import datetime, timedelta
from http.client import METHOD_NOT_ALLOWED
from random import choice, randrange
from string import digits

from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django_twilio.decorators import twilio_view
from rest_framework import status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import Alert, AlertType, Beneficiary, BeneficiaryType
from alerts.permissions import IsSameOrganization
from alerts.serializers import (
    AlertSerializer,
    AlertTypeSerializer,
    BeneficiarySerializer,
    BeneficiaryTypeSerializer,
)
from alerts.utils import EnablePartialUpdateMixin


class BeneficiaryTypeViewSet(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsSameOrganization,
    ]
    serializer_class = BeneficiaryTypeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.filter_queryset(
            BeneficiaryType.objects.filter(organization=user.organization)
        )
        return queryset


class AlertTypeViewSet(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    permission_classes = [
        IsSameOrganization,
    ]
    serializer_class = AlertTypeSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.filter_queryset(
            AlertType.objects.filter(organization=user.organization)
        )
        return queryset


class FakeAlertAPIView(APIView):
    serializer_class = AlertSerializer

    def post(self, request, format=None):
        """
        Creates a fake alert
        """

        locations = [
            (-34.654905, -58.6497804),
            (-34.676289, -58.378931),
            (-34.6497796, -58.51051807),
            (-34.6326636, -58.692194399),
        ]

        loc_pos = randrange(4)

        organization = request.user.organization
        telephone = "".join(choice(digits) for _ in range(12))
        beneficiary = Beneficiary.objects.create(
            organization=organization,
            name="Juan",
            surname="Perez",
            telephone=telephone,
            description="beneficiario en situacion de emergencia",
            company="CLA",
        )

        beneficiary.save()
        alert = Alert.objects.create(
            datetime=datetime.now(),
            beneficiary=beneficiary,
            latitude=locations[loc_pos][0],
            longitude=locations[loc_pos][1],
            organization=organization,
        )

        alert.save()
        return HttpResponse(status=200)


class BeneficiaryViewSet(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for beneficiaries
    """

    permission_classes = [
        IsSameOrganization,
    ]

    serializer_class = BeneficiarySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["telephone", "name", "surname", "enabled"]

    def get_queryset(self):
        user = self.request.user
        queryset = self.filter_queryset(
            Beneficiary.objects.filter(organization=user.organization)
        )
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


class AlertViewSet(EnablePartialUpdateMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for beneficiaries
    """

    permission_classes = [
        IsSameOrganization,
    ]

    serializer_class = AlertSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "datetime": ["lte", "gte"],
        "beneficiary_id": ["exact"],
        "state": ["exact"],
        "type": ["exact"],
    }

    def get_queryset(self):
        user = self.request.user
        queryset = self.filter_queryset(
            Alert.objects.filter(organization=user.organization)
        ).order_by("-datetime")
        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        """
        Validaciones sobre alerta:
        """
        if "state" in request.data:
            if request.data["state"] == "N":
                return Response(
                    _("Cambio de estado inválido"), status=status.HTTP_400_BAD_REQUEST
                )

            if request.data["state"] == "A":
                if instance.state != "N":
                    return Response(
                        _("Cambio de estado inválido"),
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    instance.state = "A"
                    instance.datetime_attended = timezone.now()
                    instance.operator = request.user

            if request.data["state"] == "C":
                if instance.state != "A":
                    return Response(
                        _("Cambio de estado inválido"),
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    instance.state = "C"
                    instance.datetime_closed = timezone.now()

        if "type_id" in request.data:
            try:
                type = AlertType.objects.get(
                    id=request.data["type_id"], organization=request.user.organization
                )
                instance.type = type
            except AlertType.DoesNotExist:
                return Response(
                    _("Tipo de alerta inválido"), status=status.HTTP_400_BAD_REQUEST
                )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        raise METHOD_NOT_ALLOWED(request.method)


class TwilioWebhookView(APIView):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]
    parser_classes = [FormParser]

    @method_decorator(twilio_view)
    def dispatch(self, request, *args, **kwargs):
        return super(TwilioWebhookView, self).dispatch(request, *args, **kwargs)

    def post(self, request, format=None):
        try:
            message_sid = request.data["MessageSid"]
            # El cuerpo debe tener el formato https://maps.google.com/?q=<lat>,<lng>
            body = request.data["Body"]
            telephone = request.data["From"]
        except KeyError:
            return Response(
                _("Formulario inválido, se requiere MessageSid, Body y From"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if body and "https://maps.google.com/?q=" in body:
            try:
                partition = body.split("https://maps.google.com/?q=")
                latitude, longitude = partition[1].split(",")
                data = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "telephone": telephone,
                    "message_sid": message_sid,
                }
                serializer = AlertSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(
                        _("Error creando alerta"), status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    _("Datos del SMS inválidos"), status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                _("Cuerpo del SMS inválido"), status=status.HTTP_400_BAD_REQUEST
            )


class AlertsSummaryView(GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    serializer_class = AlertSerializer

    def get(self, request):
        user = self.request.user
        queryset = self.filter_queryset(
            Alert.objects.filter(
                organization=user.organization,
                datetime__gte=datetime.now() - timedelta(days=1),
            ).order_by("-datetime")
        )
        serializer = AlertSerializer(queryset, many=True)
        return Response(serializer.data)
