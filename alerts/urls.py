from django.urls import include, path
from rest_framework.routers import DefaultRouter

from alerts.views import BeneficiaryViewSet

app_name = "alerts"

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"beneficiaries", BeneficiaryViewSet, basename="beneficiary")


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls), name="beneficiary"),
]
