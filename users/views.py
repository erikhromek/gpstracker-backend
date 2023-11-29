from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.permissions import IsAdmin, IsSameOrganization
from users.models import User

from .serializers import (
    RegisterRootSerializer,
    RegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserListAPI(generics.ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsSameOrganization,
    )

    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(organization=user.organization)
        return queryset


# Class based view to Get User Details using Token Authentication
class UserDetailAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# Class based view to register root user
class RegisterRootUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterRootSerializer


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = RegisterSerializer


class UpdateUserAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
