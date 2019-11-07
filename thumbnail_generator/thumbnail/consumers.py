import json
import boto3
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from datauri import DataURI
from .utils import \
    convert_base64_string_to_image, create_thumbnail, upload_image_to_s3


class ThumbnailConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print('connected')
        await self.accept()

    async def websocket_receive(self, event):
        data = json.loads(event['text'])
        uri = DataURI(data['image'])
        filename = data['imageName']
        filename = convert_base64_string_to_image(uri.data, filename)
        filename = create_thumbnail(filename)
        filename = upload_image_to_s3(filename)
        os.remove(filename)

    async def disconnect(self, close_code):
        pass
