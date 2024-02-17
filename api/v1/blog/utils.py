import re
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image
from django.conf import settings

from blog.models import TinyMCEPicture

new_width = 1300
suffix_allow_list = ('.jpg', '.jpeg', '.jfif', '.png', '.webp')


def download_image(src_url):
    response = requests.get(src_url)
    file = src_url.split("/")[-1]

    current_datetime = datetime.now().strftime("%Y/%m/%d")

    # Create a directory with the current date and millisecond as the name
    save_path = (Path(settings.MEDIA_ROOT) / Path('uploads') / Path(current_datetime) / file)
    save_path = make_unique_path_name(save_path, save_path.suffix)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'wb+') as destination:
        destination.write(response.content)

    return create_tinymce_picture(save_path)


def parse_and_download_images(html):
    modified_html = html
    img_urls = re.findall(r'<img.*?src="(.*?)"', html)
    for img_url in img_urls:
        # Get the source URL of the image
        match_obj = re.match(r'^(?:http)s?://', img_url, re.I | re.M)

        if match_obj:
            # Download the image and save it locally
            new_url = download_image(img_url)
        else:
            new_url = create_tinymce_picture(Path(img_url[1:]))
        modified_html = modified_html.replace(img_url, new_url, 1)
    # Return the modified HTML as a response
    return modified_html


def make_unique_path_name(image, suffix='.webp'):
    path = image.parent
    name = image.stem + suffix
    c_count = 1
    path_name = path / name
    while path_name.exists():
        path_name = path / f"{image.stem}_{c_count}{suffix}"
        c_count += 1
    return path_name


def compress_img(img_path):
    if img_path.suffix in suffix_allow_list:
        path = make_unique_path_name(img_path)
        img_file = Image.open(img_path)
        height = img_file.height
        width = img_file.width
        if width > new_width:
            height2 = int((new_width * height) / width)
            img_file = img_file.resize((new_width, height2), Image.LANCZOS)
        img_file.save(path, format='WEBP', quality=75, optimize=True)
        return path


def create_tinymce_picture(path):
    img_path = compress_img(path)
    compressed_img_path = "/" + "/".join(Path(img_path).parts[-5:])
    original_img_path = "/" + "/".join(Path(path).parts[-5:])
    TinyMCEPicture.objects.create(original=original_img_path, converted=compressed_img_path)
    return "/" + "/".join(Path(img_path).parts[-6:])
