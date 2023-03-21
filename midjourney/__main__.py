from pathlib import Path

from . import logger
from .models.config import MidjourneyCsvConfig
from .models.image import ImageEntry

PATH_TO_FILES = Path("/Users/igorzamyslov/Downloads")
GLOB_PATTERN = "midjourney*.csv"
OUTPUT_FOLDER = Path("images")
CROPPED_SUBFOLDER = "_cropped"
DIMENSIONS_CM = [(13, 18), (10, 15), (9, 13)]
DPCM = 120

config = MidjourneyCsvConfig.from_csvs(PATH_TO_FILES, GLOB_PATTERN)

for i, entry in enumerate(config.entries):
    logger.info("%s/%s", i + 1, len(config.entries))
    output_dir = OUTPUT_FOLDER
    if entry.category is not None:
        output_dir /= entry.category
    image = ImageEntry.from_url(url=entry.url,
                                prompt=entry.prompt,
                                output_dir=output_dir)
    image.save()
    for width, height in DIMENSIONS_CM:
        cropped_image = image.crop_image(width, height, DPCM, CROPPED_SUBFOLDER)
        if cropped_image.prompt:
            cropped_image.embed_prompt()
        cropped_image.save()
