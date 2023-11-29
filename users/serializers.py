from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Organization, User

# Serializer to Get User Details using Django Token Authentication


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "surname", "email", "organization"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "surname", "email", "password"]

    def validate(self, attrs):
        logged_user = self.context.get("request").user
        modified_user = User.objects.get(id=self.instance.id)
        if logged_user.organization.id != modified_user.organization.id:
            raise serializers.ValidationError(
                _("Solo se pueden modificar usuarios propios.")
            )

        if logged_user.role != "ADM" and logged_user.id != modified_user.id:
            raise serializers.ValidationError(
                _("Solo se puede modificar el usuario propio.")
            )
        return attrs


# Serializer to Register Root User
class RegisterRootSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        max_length=64, required=True, write_only=True
    )
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "name",
            "surname",
            "organization_name",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": _("La contraseña no coincide.")}
            )
        if attrs["email"]:
            if len(User.objects.filter(email=attrs["email"])) > 0:
                raise serializers.ValidationError(
                    {"email": _("El email ya se encuentra en uso.")}
                )

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            name=validated_data["name"],
            surname=validated_data["surname"],
        )
        user.set_password(validated_data["password"])
        organization = Organization.objects.create(
            name=validated_data["organization_name"], enabled=True
        )
        organization.save()
        user.role = "ADM"
        user.organization = organization
        user.save()
        return user


# Serializer to Register User
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "name", "surname")
        extra_kwargs = {
            "email": {"required": True},
            "name": {"required": True},
            "surname": {"required": True},
            "password": {"required": True},
            "password2": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": _("La contraseña no coincide.")}
            )
        if attrs["email"]:
            if len(User.objects.filter(email=attrs["email"])) > 0:
                raise serializers.ValidationError(
                    {"email": _("El email ya se encuentra en uso.")}
                )

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if not user.is_authenticated or user.role != "ADM":
                raise serializers.ValidationError(
                    _("Solo un administrador puede crear un usuario operador.")
                )
        else:
            raise serializers.ValidationError(
                _("Solo un administrador puede crear un usuario operador.")
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        root_user = request.user
        user = User.objects.create(
            email=validated_data["email"],
            name=validated_data["name"],
            surname=validated_data["surname"],
        )
        user.set_password(validated_data["password"])
        user.role = "OPS"

        user.organization = root_user.organization
        user.save()
        return user
