from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from alerts.permissions import IsAdmin, IsSameOrganization
from users.models import User

from .serializers import (
    RegisterRootSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserListAPI(generics.ListAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [
        IsSameOrganization,
    ]

    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(organization=user.organization)
        return queryset


# Class based view to Get User Details using Token Authentication
class UserDetailAPI(APIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# Class based view to register root user
class RegisterRootUserAPIView(generics.CreateAPIView):
    authentication_classes = []
    permission_classes = [
        AllowAny,
    ]
    serializer_class = RegisterRootSerializer


class RegisterUserAPIView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]
    serializer_class = RegisterSerializer


class UpdateUserAPIView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication, BasicAuthentication]
    permission_classes = [
        IsSameOrganization,
    ]

    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenVerifyResponseSerializer(serializers.Serializer):
    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenVerifyResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenBlacklistResponseSerializer(serializers.Serializer):
    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenBlacklistView(TokenBlacklistView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: TokenBlacklistResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
