# Description

The script does the following:
1. Downloads images from the provided URLs
1. Crops the middle part out of them according to the provided dimensions
1. Resizes the images according to `DPCM` parameter
1. Embeds the provided prompt on a semi-transparent background

# Environment variables

## Required
- `PATH_TO_CONFIGS` - `str (path)`, **required** - path to folder where to search for input CSV files containing URLs and prompts

## Optional
- `CONFIG_CLASS` - `str`, default: `BasicConfig` - defines which class to use for parsing the configs, available:
  - `BasicConfig`
  - `MidjourneyConfig`
- `GLOB_PATTERN` - `str`, default: `photos.csv` - glob pattern to use to find the config files
- `OUTPUT_FOLDER` - `str (path)`, default: `images` - where to store downloaded files
- `CROPPED_SUBFOLDER` - `str`, default: `_cropped` - where to store cropped files (under `OUTPUT_FOLDER`)
- `SPLIT_BY_CATEGORY` - `int`, default: `1` - set it to `0` to put all files into the `OUTPUT_FOLDER` directly
- `CROP_DIMENSIONS` - `json`, default: `[[10, 15]]` - defines how to crop the files (in cm), multiple dimensions can be provided
- `DPCM` - `int`, default: `120` - dots per centimeter, will resize the photos to `dimensions * dpcm`

# Running

## Install requirements

```bash
pip install -r requirements.txt
```

## Run

1. Set all the necessary environment variables
1. Run the following code
    ```bash
    python -m photo_handler
    ```
