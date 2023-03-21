from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional, Type, TypeVar

import requests
from PIL import Image, ImageDraw, ImageFont

from midjourney import logger

CLS = TypeVar("CLS")


@dataclass
class ImageEntry:
    image: Image
    filename: str
    prompt: Optional[str]
    output_dir: Path
    extension: str = "png"

    @classmethod
    def from_url(cls: Type[CLS], url: str, prompt: Optional[str],
                 output_dir: Path, filename: str = None,
                 extension: str = None) -> CLS:
        if filename is None:
            filename = f"{abs(hash(url))}"
        if extension is None:
            extension = cls.extension

        return cls(image=cls.download(url),
                   prompt=prompt,
                   output_dir=output_dir,
                   filename=filename,
                   extension=extension)

    @staticmethod
    def download(url: str) -> Image:
        response = requests.get(
            url,
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
        return Image.open(BytesIO(response.content))

    def embed_prompt(self, font_path="Helvetica", rectangle_size=(960, 200), font_size=40):
        # Create drawing context
        draw = ImageDraw.Draw(self.image, "RGBA")

        # Set font
        font = ImageFont.truetype(font_path, font_size)

        # Calculate text size and position
        max_text_width = rectangle_size[0] - 40  # 10px padding on each side
        lines = []
        words = self.prompt.split()
        while words and len(lines) < 4:
            line = ""
            while words and font.getsize(line + words[0])[0] <= max_text_width:
                line += words.pop(0) + " "
            # if not words and font.getsize(line.rstrip())[0] <= max_text_width:
            #     line = line.rstrip()
            line = line.rstrip()
            if len(lines) == 3:
                line = line.rsplit(" ", 1)[0] + " ..."
            lines.append(line)

        text_height = len(lines) * font.getsize(lines[0])[1]
        x = (self.image.width - rectangle_size[0]) // 2
        y = (self.image.height - rectangle_size[1]) - 60
        text_y = y + (rectangle_size[1] - text_height) // 2

        # Calculate rectangle position
        rectangle_x = x
        rectangle_y = y

        # Draw rectangle
        draw.rounded_rectangle(
            ((rectangle_x, rectangle_y),
             (rectangle_x + rectangle_size[0], rectangle_y + rectangle_size[1])),
            fill=(0, 0, 0, 127),
            outline=None,
            radius=30,
        )

        # Draw text
        for line in lines:
            line_width, _ = font.getsize(line.rstrip())
            line_x = x + (rectangle_size[0] - line_width) // 2
            draw.text(
                (line_x, text_y),
                line.rstrip(),
                fill=(255, 255, 255, 255),
                font=font,
                align="left",
                spacing=0,
            )
            text_y += font.getsize(line)[1]

    def crop_image(self: CLS, width_cm: int, height_cm: int, dpcm: int,
                   subdir_name: str = "_cropped") -> CLS:
        """
        function to crop image to given size,
        taking the middle part and resize it according to the dpcm
        """
        img = self.image.copy()
        height = height_cm * dpcm
        width = width_cm * dpcm
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

        return ImageEntry(image=new_img,
                          filename=f"{self.filename}_{width_cm}x{height_cm}",
                          prompt=self.prompt,
                          output_dir=self.output_dir / subdir_name)

    def save(self):
        logger.info(f"Saving {self.filename} in {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{self.filename}.{self.extension}"
        with output_path.open("wb") as file:
            self.image.save(file)
