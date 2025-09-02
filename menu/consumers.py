# menu/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChefConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # For a multi-tenant app, the frontend would provide the restaurant slug
        # For now, we assume a Super Chef view or need a way to pass this.
        # Let's create a dynamic group name. The frontend will need to connect to ws/chef/restaurant-slug/
        self.restaurant_slug = self.scope['url_route']['kwargs']['restaurant_slug']
        self.group_name = f'chef_notifications_{self.restaurant_slug}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This method is called when a message is sent to the group
    async def send_new_order(self, event):
        order_data = event['data']
        # Send the order data to the connected client (the chef's browser)
        await self.send(text_data=json.dumps(order_data))


class CustomerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.bill_id = self.scope['url_route']['kwargs']['bill_id']
        self.bill_group_name = f'customer_{self.bill_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.bill_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.bill_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_status_update(self, event):
        data = event['data']
        # Send message to WebSocket
        await self.send(text_data=json.dumps(data))