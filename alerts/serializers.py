from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from alerts.models import Alert, AlertType, Beneficiary, BeneficiaryType
from alerts.utils import only_int


class BeneficiaryTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(max_length=8, required=True)
    description = serializers.CharField(max_length=32, required=True)

    class Meta:
        model = BeneficiaryType
        fields = [
            "id",
            "code",
            "description",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        try:
            existing_type = BeneficiaryType.objects.get(
                code=validated_data["code"], organization=request.user.organization
            )
            if existing_type:
                raise serializers.ValidationError(
                    _(
                        "El codigo utilizado para el tipo de beneficiario ya se encuentra creado."
                    )
                )
        except BeneficiaryType.DoesNotExist:
            pass
        request = self.context.get("request")
        type = BeneficiaryType.objects.create(
            code=validated_data["code"],
            description=validated_data["description"],
            organization=request.user.organization,
        )
        type.save()
        return type


class AlertTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    code = serializers.CharField(max_length=8, required=True)
    description = serializers.CharField(max_length=32, required=True)

    class Meta:
        model = AlertType
        fields = [
            "id",
            "code",
            "description",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        try:
            existing_type = AlertType.objects.get(
                code=validated_data["code"], organization=request.user.organization
            )
            if existing_type:
                raise serializers.ValidationError(
                    _(
                        "El codigo utilizado para el tipo de alerta ya se encuentra creado."
                    )
                )
        except AlertType.DoesNotExist:
            pass
        request = self.context.get("request")
        type = AlertType.objects.create(
            code=validated_data["code"],
            description=validated_data["description"],
            organization=request.user.organization,
        )
        type.save()
        return type


class BeneficiarySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64, required=True)
    surname = serializers.CharField(max_length=64, required=True)
    telephone = serializers.CharField(
        max_length=32, required=True, validators=[only_int]
    )
    company = serializers.ChoiceField(
        choices=Beneficiary.COMPANY_CHOICES, default="OTH", required=False
    )
    enabled = serializers.BooleanField(default=True)
    type_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = Beneficiary
        fields = [
            "id",
            "name",
            "surname",
            "telephone",
            "enabled",
            "type_id",
            "company",
            "description",
        ]

    def create(self, validated_data):
        try:
            existing_beneficiary = Beneficiary.objects.get(
                telephone=validated_data["telephone"]
            )
            if existing_beneficiary:
                raise serializers.ValidationError(
                    _(
                        "El teléfono se encuentra actualmente en uso por otro beneficiario."
                    )
                )
        except Beneficiary.DoesNotExist:
            pass
        request = self.context.get("request")
        beneficiary = Beneficiary.objects.create(
            name=validated_data["name"],
            telephone=validated_data["telephone"],
            surname=validated_data["surname"],
            description=validated_data["description"],
            company=validated_data["company"],
            enabled=validated_data["enabled"],
            organization=request.user.organization,
        )
        if "type_id" in validated_data:
            try:
                type = BeneficiaryType.objects.get(
                    id=validated_data["type_id"], organization=request.user.organization
                )
                beneficiary.type = type
            except BeneficiaryType.DoesNotExist:
                raise serializers.ValidationError(
                    _("El tipo de beneficiario es inválido.")
                )
        beneficiary.save()
        return beneficiary


class AlertSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    message_sid = serializers.CharField(max_length=34, required=False)
    beneficiary_id = serializers.IntegerField(allow_null=True, required=False)
    telephone = serializers.CharField(
        max_length=32, required=True, validators=[only_int]
    )
    datetime = serializers.DateTimeField(required=False)
    datetime_attended = serializers.DateTimeField(required=False)
    datetime_closed = serializers.DateTimeField(required=False)
    latitude = serializers.CharField(max_length=64, required=True)
    longitude = serializers.CharField(max_length=64, required=True)
    state = serializers.ChoiceField(
        choices=Alert.ALERT_STATUS, required=False, default="N"
    )
    operator_id = serializers.IntegerField(allow_null=True, required=False)
    observations = serializers.CharField(max_length=512, required=False)
    type_id = serializers.IntegerField(allow_null=True, required=False)

    class Meta:
        model = Alert
        fields = [
            "id",
            "datetime",
            "datetime_attended",
            "datetime_closed",
            "beneficiary_id",
            "telephone",
            "latitude",
            "longitude",
            "state",
            "operator_id",
            "observations",
            "type_id",
            "message_sid",
        ]

    def create(self, validated_data):
        existing_beneficiary = None
        try:
            existing_beneficiary = Beneficiary.objects.get(
                telephone=validated_data["telephone"],
                enabled=True,
            )
        except Beneficiary.DoesNotExist:
            raise serializers.ValidationError(
                _("El beneficiario no existe o se encuentra desactivado.")
            )

        if existing_beneficiary:
            alert = Alert.objects.create(
                beneficiary=existing_beneficiary,
                datetime=timezone.now(),
                latitude=validated_data["latitude"],
                longitude=validated_data["longitude"],
                state="N",
                organization=existing_beneficiary.organization,
            )
        alert.save()
        return alert
