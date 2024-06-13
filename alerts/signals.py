from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from alerts.models import Alert
from alerts.serializers import AlertSerializer


@receiver(signal=post_save, sender=Alert)
def alert_save_signal(sender, instance, created, **kwargs):
    if created:
        serializer = AlertSerializer(instance)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"{instance.organization.id}",
            {
                "type": "alert_message",
                "message": serializer.data,
            },
        )
