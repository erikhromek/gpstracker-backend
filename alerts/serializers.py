from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from alerts.models import Alert, Beneficiary, BeneficiaryType
from alerts.utils import only_int


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

        try:
            if "type_id" in validated_data:
                type = BeneficiaryType.objects.get(id=validated_data["type_id"])
                beneficiary.type = type
        except BeneficiaryType.DoesNotExist:
            raise serializers.ValidationError(_("El tipo de beneficiario es inválido."))
        beneficiary.save()
        return beneficiary


class AlertSerializer(serializers.Serializer):
    class Meta:
        model = Alert
