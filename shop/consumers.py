import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    print("CONNECT METHOD STARTED")

    async def connect(self):
        print("Attempting to connect...")
        try:
            self.username = self.scope["url_route"]["kwargs"]["username"]
            print(f"Username extracted: {self.username}")

            self.group_name = f"notifications_{self.username}"

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            self.send(text_data=json.dumps({"username": self.username}))
            await self.accept()
            print("Connection accepted.")
        except KeyError:
            print("Error: 'username' not found in URL kwargs.")
            await self.close()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "content": {"message": message},
            },
        )
        print(message)

    async def send_notification(self, event):
        try:
            message = event["content"]["message"]
            await self.send(text_data=json.dumps({"message": message}))
        except KeyError as e:
            print(f"KeyError in send_notification: {e}. Event: {event}")
