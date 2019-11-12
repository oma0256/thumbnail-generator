import boto3
import os
from celery import shared_task
from celery.signals import task_success, task_prerun
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings


@shared_task
def upload_image_to_s3(filename, group_name):
    s3_client = boto3.client(
        's3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    try:
        file_path = f'{settings.PROJECT_DIR}/{filename}'
        bucket = os.getenv('BUCKET')
        response = s3_client.upload_file(file_path, bucket, filename)
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
    file_path = f'{settings.PROJECT_DIR}/{filename}'
    os.remove(file_path)
    channel_layer = get_channel_layer()
    BUCKET_NAME = os.getenv('BUCKET')
    thumbnail = f'https://{BUCKET_NAME}.s3.amazonaws.com/{filename}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'upload_complete',
            'thumbnail': thumbnail,
            'filename': filename
        }
    )
