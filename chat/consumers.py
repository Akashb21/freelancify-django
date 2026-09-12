import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()

        if message_text and self.scope['user'].is_authenticated:
            msg_obj = await self.save_message(message_text)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': msg_obj['text'],
                    'sender': msg_obj['sender'],
                    'created_at': msg_obj['created_at'],
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'created_at': event['created_at'],
        }))

    @database_sync_to_async
    def save_message(self, text):
        from .models import Conversation, Message
        conv = Conversation.objects.get(pk=self.conversation_id)
        msg = Message.objects.create(
            conversation=conv,
            sender=self.scope['user'],
            text=text
        )
        conv.save() # update timestamp
        return {
            'text': msg.text,
            'sender': msg.sender.username,
            'created_at': msg.created_at.strftime('%H:%M')
        }
