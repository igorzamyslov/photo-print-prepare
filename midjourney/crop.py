import os
from typing import List, Tuple

from PIL import Image
from . import logger


def crop_image(image_path, width, height):
    """ function to crop image to given size, taking the middle part """
    with Image.open(image_path) as img:
        # get original image size and aspect ratio
        org_width, org_height = img.size
        org_ratio = org_width / org_height

        # get new size and coordinates for cropping
        if org_width > org_height:
            width, height = height, width

        if width / height < org_ratio:
            # crop height to fit
            new_height = org_height
            new_width = int(org_height * (width / height))
            x1 = int((org_width - new_width) / 2)
            y1 = 0
            x2 = x1 + new_width
            y2 = new_height
        else:
            # crop width to fit
            new_height = int(org_width * (height / width))
            new_width = org_width
            x1 = 0
            y1 = int((org_height - new_height) / 2)
            x2 = new_width
            y2 = y1 + new_height

        # crop image
        new_img = img.crop((x1, y1, x2, y2))

        # resize image to specified dimensions
        new_img = new_img.resize((width, height))

        # return cropped and resized image
        return new_img


def crop_all(input_path: str, dimensions_cm: List[Tuple[int, int]],
             output_folder: str = "_cropped", dpcm: int = 120):
    # loop through all image files in input directory
    os.makedirs(os.path.join(input_path, output_folder), exist_ok=True)
    logger.info("Cropping images in %s", input_path)
    files = os.listdir(input_path)
    for i, filename in enumerate(files):
        logger.info("%s/%s", i + 1, len(files))
        if filename.endswith(('.jpg', '.jpeg', '.png', ".webp")):
            for width_cm, height_cm in dimensions_cm:
                width = width_cm * dpcm
                height = height_cm * dpcm
                # get full path of input image
                image_path = os.path.join(input_path, filename)
                # crop image
                cropped_img = crop_image(image_path, width, height)
                # save
                # create output filename
                out_filename = os.path.splitext(filename)[0] + f"_{width_cm}x{height_cm}.png"
                output_path = os.path.join(input_path, output_folder, out_filename)
                cropped_img.save(output_path)