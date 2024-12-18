#!/usr/bin/env python3
import requests
import json
import os
from urllib.parse import urlparse
import argparse
import glob
import random
import logging

def read_credentials(path):
    with open(path) as f:
        return json.loads(f.read())


def get_pixabay_images(credentials):
    url = 'https://pixabay.com/api/'

    params = dict(
        key=credentials["apikey"],
        image_type="photo",
        category="nature",
        min_width=1920,
        min_height=1080,
        editors_choice=True,
    )

    resp = requests.get(url=url, params=params)
    return resp.json() 

def write_pixabay(data):
    with open("pixabay.json", "w") as f:
        f.write(json.dumps(data))

def read_pixabay():
    with open("pixabay.json", "r") as f:
        return json.loads(f.read())
    

def download_file(url, output):
    response = requests.get(url, stream=True)
    with open(output, mode="wb") as file:
        for chunk in response.iter_content(chunk_size=10 * 1024):
            file.write(chunk)

def download_new_picture(logger, output_dir_path, hits):
    for hit in hits:
        hit_directory = os.path.join(output_dir_path,str(hit["id"]))
        if not os.path.exists(hit_directory):
            os.makedirs(hit_directory,exist_ok=True)
            with open(os.path.join(hit_directory,"hit.json"), "w") as f:
                f.write(json.dumps(hit))

            page_url = urlparse(hit["pageURL"])
            page_name = [l for l in str.split(page_url.path,'/') if l.strip()][-1]

            download_url= hit["largeImageURL"]
            download_name = [l for l in str.split(urlparse(download_url).path,'/') if l.strip()][-1]
            _root, extension = os.path.splitext(download_name)

            output_path = os.path.join(hit_directory, page_name + extension)
            download_file(download_url, output_path)

            logger.info(f"Downloaded: {output_path}")

            return output_path
        
    return None


def get_random_picture(dir):
    extensions = ('.jpg', '.png')
    dir_pattern = '/**/*'
    files_list = []
    for ext in extensions:
        pattern = f"{dir}{dir_pattern}{ext}"
        files_list.extend(glob.glob(pattern, recursive=True))

    if len(files_list) > 0:
        return random.choice(files_list)
    else:
        return ""


# credentials = read_credentials(".credentials.json")
# pixabay = get_pixabay_images(credentials)
# write_pixabay(pixabay)
# pixabay = read_pixabay()
# output_path = download_new_picture("photos", pixabay["hits"])
# print(output_path)

logger = logging.getLogger()
parser = argparse.ArgumentParser(
                    prog='pixabay Downloader',
                    description='This script downloads pixabay picutes')

parser.add_argument('credentials_file')
parser.add_argument('ouput_folder')
args = parser.parse_args()
output_path = None

try:
    credentials = read_credentials(args.credentials_file)
    pixabay = get_pixabay_images(credentials)
    output_path = download_new_picture(logger, args.ouput_folder, pixabay["hits"])
except Exception as e:
   logger.error('Error at %s', 'division', exc_info=e)

if not output_path:
    output_path = get_random_picture(args.ouput_folder)

if not output_path:
    logger.error('Could not open a picture in %s', args.ouput_folder)

print(output_path)

