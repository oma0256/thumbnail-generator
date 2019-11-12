import os
from PIL import Image


def convert_base64_string_to_image(base64_string, filename):
    with open(filename, 'wb') as f:
        f.write(base64_string)
    return filename


def create_thumbnail(filename):
    size = 200, 200
    try:
        image = Image.open(filename)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(filename)
        return filename
    except Exception as e:
        print(e)
