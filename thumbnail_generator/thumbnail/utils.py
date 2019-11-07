import boto3
import os
from PIL import Image


def convert_base64_string_to_image(base64_string, filename):
    with open(filename, 'wb') as f:
        f.write(base64_string)
    return filename


def create_thumbnail(filename):
    size = 20, 20
    try:
        image = Image.open(filename)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(filename)
        return filename
    except:
        print('Failed to create thumbnail')


def upload_image_to_s3(filename):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(
            filename, "first-bucket-oma0256", filename)
        return filename
    except:
        print('Image upload failed')
