from django.urls import path
from rest_framework.routers import DefaultRouter

from alerts.views import (
    AlertsSummaryView,
    AlertTypeViewSet,
    AlertViewSet,
    BeneficiaryTypeViewSet,
    BeneficiaryViewSet,
    FakeAlertAPIView,
    TwilioWebhookView,
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
    path("twilio-webhook/", TwilioWebhookView.as_view(), name="twilio-webhook"),
    path("alerts-summary/", AlertsSummaryView.as_view(), name="alerts-summary"),
    path("dummy-alert/", FakeAlertAPIView.as_view(), name="dummy-alert"),
]

urlpatterns += router.urls
