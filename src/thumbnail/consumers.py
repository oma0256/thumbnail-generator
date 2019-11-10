import json
import boto3
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from datauri import DataURI
from celery.signals import task_success
from .utils import \
    convert_base64_string_to_image, create_thumbnail
from .tasks import upload_image_to_s3


class ThumbnailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = str(uuid.uuid4())
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def websocket_receive(self, event):
        data = json.loads(event['text'])
        uri = DataURI(data['image'])
        filename = data['imageName']
        filename = convert_base64_string_to_image(uri.data, filename)
        filename = create_thumbnail(filename)
        upload_image_to_s3.delay(filename, self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def upload_complete(self, event):
        await self.send(json.dumps({'thumbnail': event['thumbnail']}))
