# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer,AsyncJsonWebsocketConsumer
from ...models import *


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json['text']
        order_id = text_data_json['order_id']
        print("Order id is :" , order_id)
        _id = text_data_json['_id']
        user = text_data_json['user']
        print("User info is ",user)
        order = Order.objects.get(id=order_id)
        #user = order.delivery_boy
        print("User is ",user)

        # Send text to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_text',
                '_id': _id,
                'text': text,
                'user': {
                '_id': user['_id'],
                'name': user['name'],
                }
            }
        )

    # Receive text from room group
    def chat_text(self, event):
        text = event['text']
        _id = event['_id']
        user = event['user']

        # Send text to WebSocket
        self.send(text_data=json.dumps({
        '_id': _id,
        'text': text,
        'user': user
        }))

class DeliveryBoyLocationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'location_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        location = text_data_json['location']
        deliveryBoy_id = text_data_json['deliveryBoy_id']
        #order_id = text_data_json['order_id']
        if deliveryBoy_id is not None:
            obj = DeliveryBoy.objects.get(id=deliveryBoy_id).user
            print(location)
            obj.latitude = location['latitude']
            obj.longitude = location['longitude']
            obj.save()
        # Send text to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,{
                'type': 'location_coords',
                'location': location,
            }
        )

    # Receive text from room group
    def location_coords(self, event):
        location = event['location']
        # Send text to WebSocket
        self.send(text_data=json.dumps({
        'location': location,
        }))    


class OrderConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'orders'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        text = text_data_json['action']
        orders = Order.objects.all()
        if text == "LIST":
            await (self.send(orders))
        # Send text to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,{
        #         'type': 'location_coords',
        #         'text': text,
        #     }
        # )

    # Receive text from room group
    # def location_coords(self, event):
    #     text = event['text']
    #     # Send text to WebSocket
    #     self.send(text_data=json.dumps({
    #     'text': text,
    #     }))    


