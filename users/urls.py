from django.urls import path
from rest_framework.authtoken import views

from .views import (
    RegisterRootUserAPIView,
    RegisterUserAPIView,
    UpdateUserAPIView,
    UserDetailAPI,
    UserListAPI,
)

app_name = "users"

urlpatterns = [
    path("users", UserListAPI.as_view(), name="list"),
    path("users/details", UserDetailAPI.as_view(), name="details"),
    path("users/admin", RegisterRootUserAPIView.as_view(), name="register-admin"),
    path("users/operator", RegisterUserAPIView.as_view(), name="register-user"),
    path("users/<int:pk>/", UpdateUserAPIView.as_view(), name="update"),
    path("login", views.obtain_auth_token, name="login"),
]
