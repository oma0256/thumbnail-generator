import boto3
import os
from celery import shared_task
from celery.signals import task_success, task_prerun
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task
def upload_image_to_s3(filename, group_name):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            filename, "first-bucket-oma0256", filename)
        return {'filename': filename, 'group_name': group_name}
    except Exception as e:
        print(e)


@task_prerun.connect(sender=upload_image_to_s3)
def image_processing_started(sender, **kwargs):
    channel_layer = get_channel_layer()
    group_name = kwargs['args'][1]
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'processing_image',
            'message': 'Processing image'
        }
    )


@task_success.connect(sender=upload_image_to_s3)
def thumbnail_upload_complete(sender, result, **kwargs):
    group_name = result['group_name']
    filename = result['filename']
    os.remove(filename)
    channel_layer = get_channel_layer()
    thumbnail = f'https://first-bucket-oma0256.s3.amazonaws.com/{filename}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'upload_complete',
            'thumbnail': thumbnail,
            'filename': filename
        }
    )
