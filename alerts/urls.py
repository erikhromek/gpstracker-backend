from django.urls import include, path
from rest_framework.routers import DefaultRouter

from alerts.views import (
    AlertTypeViewSet,
    AlertViewSet,
    BeneficiaryTypeViewSet,
    BeneficiaryViewSet,
)

app_name = "alerts"

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"beneficiaries", BeneficiaryViewSet, basename="beneficiary")
router.register(
    r"beneficiary-types", BeneficiaryTypeViewSet, basename="beneficiary-type"
)
router.register(r"alerts", AlertViewSet, basename="alert")
router.register(r"alert-types", AlertTypeViewSet, basename="alert-type")


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
