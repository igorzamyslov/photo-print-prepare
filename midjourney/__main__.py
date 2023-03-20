from pathlib import Path

from . import logger
from .crop import crop_all
from .download import download_all
from .embed_text import embed_text_in_rectangle

PATH_TO_FILES = Path("/Users/igorzamyslov/Downloads")
GLOB_PATTERN = "midjourney*.csv"
OUTPUT_FOLDER = "images"
CROPPED_SUBFOLDER = "_cropped"
DIMENSIONS_CM = [(13, 18), (10, 15), (9, 13)]

download_all(PATH_TO_FILES, GLOB_PATTERN, OUTPUT_FOLDER)

for category_path in Path(OUTPUT_FOLDER).iterdir():
    if not category_path.is_dir():
        continue
    crop_all(str(category_path), dimensions_cm=DIMENSIONS_CM,
             output_folder=CROPPED_SUBFOLDER)

for category_path in Path(OUTPUT_FOLDER).iterdir():
    logger.info("Embedding text in %s", category_path)
    if not category_path.is_dir():
        continue
    files = list((category_path / CROPPED_SUBFOLDER).iterdir())
    for i, image_path in enumerate(files):
        logger.info("%s/%s", i + 1, len(files))
        if image_path.suffix != ".png":
            continue
        text_file = category_path / f"{image_path.stem.rsplit('_', 1)[0]}.txt"
        embed_text_in_rectangle(image_path, text_file.read_text())
