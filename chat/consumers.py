import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.utils import timezone

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        self.room_group_name = 'chat_%s' % self.id
        
        # join room group
        async_to_sync(self.channel_layer.group_add)(
                      self.room_group_name,
                      self.channel_name
        )
        self.accept()   #accept connection

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
                      self.room_group_name,
                      self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()

        #send message to the room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )

    # receive message from the room group
    def chat_message(self, event):
    # Send message to the WebSocket
        self.send(text_data=json.dumps(event)) 