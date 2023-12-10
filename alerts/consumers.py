import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class AlertConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.organization_group = self.scope["url_route"]["kwargs"]["organization_id"]

        if self.user.organization.id == self.organization_group:
            async_to_sync(self.channel_layer.group_add)(
                str(self.organization_group), self.channel_name
            )
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        pass

    def alert_message(self, event, type="alert_message"):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
