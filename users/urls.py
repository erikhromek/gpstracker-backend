from django.urls import path
from rest_framework.authtoken import views

from .views import RegisterRootUserAPIView, RegisterUserAPIView, UserDetailAPI

app_name = "users"

urlpatterns = [
    path("get-details", UserDetailAPI.as_view()),
    path("register-admin", RegisterRootUserAPIView.as_view(), name="register-admin"),
    path("register-user", RegisterUserAPIView.as_view(), name="register-user"),
    path("login", views.obtain_auth_token, name="login"),
]
