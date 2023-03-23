import json
import os
from pathlib import Path

from . import logger
from .models.configs import CONFIG_CLASSES
from .models.image import ImageEntry

PATH_TO_CONFIGS = Path(os.environ.get("PATH_TO_CONFIGS"))
CONFIG_CLASS = os.environ.get("CONFIG_CLASS", "BasicConfig")
GLOB_PATTERN = os.environ.get("GLOB_PATTERN", "photos.csv")
OUTPUT_FOLDER = Path(os.environ.get("OUTPUT_FOLDER", "images"))
CROPPED_SUBFOLDER = os.environ.get("CROPPED_SUBFOLDER", "_cropped")
SPLIT_BY_CATEGORY = bool(int(os.environ.get("SPLIT_BY_CATEGORY", 1)))
CROP_DIMENSIONS = json.loads(os.environ.get("CROP_DIMENSIONS", "[[10, 15]]"))
DPCM = int(os.environ.get("DPCM", 120))

ConfigClass = CONFIG_CLASSES[CONFIG_CLASS]
config = ConfigClass.from_csvs(PATH_TO_CONFIGS, GLOB_PATTERN)

for i, entry in enumerate(config.entries):
    logger.info("%s/%s", i + 1, len(config.entries))
    output_dir = OUTPUT_FOLDER
    if SPLIT_BY_CATEGORY and entry.category is not None:
        output_dir /= entry.category
    image = ImageEntry.from_url(url=entry.url,
                                prompt=entry.prompt,
                                output_dir=output_dir)
    image.save()
    for width, height in CROP_DIMENSIONS:
        cropped_image = image.crop_image(width, height, DPCM, CROPPED_SUBFOLDER)
        if cropped_image.prompt:
            cropped_image.embed_prompt()
        cropped_image.save()
