import boto3
import os
from celery import shared_task
from celery.signals import task_success
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def upload_image_to_s3(filename, group_name):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            filename, "first-bucket-oma0256", filename)
        return {'filename': filename, 'group_name': group_name}
    except:
        print('Image upload failed')


@task_success.connect(sender=upload_image_to_s3)
def please_run(sender, result, **kwargs):
    group_name = result['group_name']
    filename = result['filename']
    os.remove(filename)
    channel_layer = get_channel_layer()
    thumbnail = f'https://first-bucket-oma0256.s3.amazonaws.com/{filename}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'upload_complete',
            'thumbnail': thumbnail
        }
    )
