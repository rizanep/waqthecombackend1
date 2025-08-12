import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    print("CONNECT METHOD STARTED")

    async def connect(self):
        print("Attempting to connect...")
        try:
            self.username = self.scope["url_route"]["kwargs"]["username"]
            print(f"Username extracted: {self.username}")

            self.group_name = f"notifications_{self.username}"  # ✅ important fix

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
        # ✅ FIX: Check if the attribute exists before using it
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "content": {"message": message},  # nested payload
            },
        )
        print(message)

    async def send_notification(self, event):
        try:
            # Access the message from the nested 'content' dictionary
            message = event["content"]["message"]
            await self.send(text_data=json.dumps({"message": message}))
        except KeyError as e:
            # Handle cases where the key might be missing
            print(f"KeyError in send_notification: {e}. Event: {event}")
            # Do not send a message if it's malformed to avoid crashing
