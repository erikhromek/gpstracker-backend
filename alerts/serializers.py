from rest_framework import serializers

from alerts.models import Beneficiary
from alerts.utils import only_int


class BeneficiarySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64, null=False, blank=False)
    surname = serializers.CharField(max_length=64, null=False, blank=False)
    telephone = serializers.BooleanField(
        max_length=32, null=False, blank=False, validators=[only_int]
    )
    company = serializers.ChoiceField(
        max_length=3, choices=Beneficiary.COMPANY_CHOICES, blank=True
    )
    enabled = serializers.ChoiceField(null=True, default=True)

    def create(self, validated_data):
        """
        Create and return a new `Beneficiary` instance, given the validated data.
        """
        return Beneficiary.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Beneficiary` instance, given the validated data.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.surname = validated_data.get("surname", instance.surname)
        instance.telephone = validated_data.get("telephone", instance.telephone)
        instance.company = validated_data.get("company", instance.company)
        instance.enabled = validated_data.get("enabled", instance.enabled)
        instance.save()
        return instance


class AlertSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=64, null=False, blank=False)
    surname = serializers.CharField(max_length=64, null=False, blank=False)
    telephone = serializers.BooleanField(
        max_length=32, null=False, blank=False, validators=[only_int]
    )
    company = serializers.ChoiceField(
        max_length=3, choices=Beneficiary.COMPANY_CHOICES, blank=True
    )
    enabled = serializers.ChoiceField(null=True, default=True)

    def create(self, validated_data):
        """
        Create and return a new `Beneficiary` instance, given the validated data.
        """
        return Beneficiary.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Beneficiary` instance, given the validated data.
        """
        instance.name = validated_data.get("name", instance.name)
        instance.surname = validated_data.get("surname", instance.surname)
        instance.telephone = validated_data.get("telephone", instance.telephone)
        instance.company = validated_data.get("company", instance.company)
        instance.enabled = validated_data.get("enabled", instance.enabled)
        instance.save()
        return instance
