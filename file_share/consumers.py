import json
from django.contrib.contenttypes.models import ContentType
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebSocketConsumer
from file_share.models import Comment, Post


class CommentsConsumer(AsyncWebSocketConsumer):

    async def connect(self):
        self.post_id = self['url_route']['kwargs']['post_id']
        self.post_group_name = 'post_%s' % self.post_id

        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, code):
        await self.channel_layer.discard(self.post_group_name, self.channel_name)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comment = text_data_json['text']
        new_comment = await self.create_new_comment(comment)
        data = {
            'author': new_comment.author.username,
            'created_at': new_comment.created_at.strftime('%Y-%m-%d %H:%m'),
            'text': new_comment.text
        }

        await self.channel_layer.group_send(
            self.post_group_name, 
            {
                'type': 'new_comment',
                'message': data, 
            }
        )

    async def new_comment(self, event): 
        message = event['message']
        await self.send(
            text_data = json.dumps(
                {
                    'message' : message,
                }
            )
        )

    @database_sync_to_async
    def create_new_comment(self, text): 
        ct = ContentType.objects.get_for_model(Post)
        new_comment = Comment.objects.create(
            author = self.scope['user'],
            content = text,
            content_type = ct,
            object_id = int(self.post_id)
        )

        return new_comment