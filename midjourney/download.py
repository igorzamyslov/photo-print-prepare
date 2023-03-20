import csv
import os
import urllib.request
from io import BytesIO
from pathlib import Path
from time import sleep
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from PIL import Image

from . import logger


def get_csv_content(path_to_files: Path, glob_pattern: str) -> List[Tuple[str, str, str]]:
    # loop through each CSV file
    content = set()
    for file in path_to_files.glob(glob_pattern):
        # open the file
        with file.open(newline='') as csvfile:
            # create a reader object
            reader = csv.DictReader(csvfile)

            # loop through each row in the file
            for row in reader:
                # extract the category from the URL
                category = str(urlparse(row["web-scraper-start-url"]).path).split("/")[-2]
                # clean up url
                url = row["image-src"]
                if url.startswith("/_next"):
                    url = extract_url_parameter(url)
                    if url is None:
                        logger.warning("Unknown URL format: %s", row["image-src"])
                        continue
                url = transform_url(url)
                # do something with the data in the row
                content.add((category, row["prompt"], url))
    return sorted(content)


def extract_url_parameter(url_string) -> Optional[str]:
    # Parse the URL string and get the "url" parameter value
    parsed_url = urllib.parse.urlparse(url_string)
    url_param = urllib.parse.parse_qs(parsed_url.query).get('url', None)

    if url_param:
        # Decode the URL parameter value
        decoded_url = urllib.parse.unquote(url_param[0])
        return decoded_url

    return None


def transform_url(url) -> str:
    filename = url.rsplit('/', 1)[-1]
    if '_' in filename:
        parts = filename.split('.')
        name_parts = parts[0].split('_')
        if len(name_parts) > 2:
            name_parts = name_parts[0:2]
        filename = '_'.join(name_parts) + '.' + parts[-1]
        return url.rsplit('/', 1)[0] + '/' + filename
    else:
        return url


def download_image(category: str, prompt: str, image_url: str, output_folder: str):
    """ Download + convert the image to png"""
    # create folder for the category if it doesn't exist
    os.makedirs(os.path.join(output_folder, category), exist_ok=True)
    filename = f"{abs(hash(image_url))}.png"

    # download the image
    response = requests.get(
        image_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) "
                          "Gecko/20100101 Firefox/110.0",
            "Accept": "text/html,application/xhtml+xml,"
                      "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        })

    image_path = os.path.join(output_folder, category, filename)
    with open(image_path, "wb") as fp:
        Image.open(BytesIO(response.content)).save(fp)

    # save the prompt as a text file
    prompt_path = os.path.join(output_folder, category, os.path.splitext(filename)[0] + ".txt")
    with open(prompt_path, "w") as f:
        f.write(prompt)


def download_all(path_to_files: Path, glob_pattern: str, output_folder: str = "images"):
    content = get_csv_content(path_to_files, glob_pattern)
    for i, (category, prompt, url) in enumerate(content):
        logger.info("%s/%s", i + 1, len(content))
        download_image(category, prompt, url, output_folder=output_folder)
        sleep(1)
