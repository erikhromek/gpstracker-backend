from django.urls import path

from alerts import consumers

websocket_urlpatterns = [
    path(
        "ws/alerts/organization-<int:organization_id>/",
        consumers.AlertConsumer.as_asgi(),
        name="alert-consumer",
    ),
]
