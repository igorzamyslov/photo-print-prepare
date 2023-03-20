from PIL import Image, ImageDraw, ImageFont


def embed_text_in_rectangle(image_path, text, font_path="Helvetica",
                            rectangle_size=(960, 200), font_size=40):
    # Open image
    image = Image.open(image_path)

    # Create drawing context
    draw = ImageDraw.Draw(image, "RGBA")

    # Set font
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text size and position
    max_text_width = rectangle_size[0] - 40  # 10px padding on each side
    lines = []
    words = text.split()
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
    x = (image.width - rectangle_size[0]) // 2
    y = (image.height - rectangle_size[1]) - 60
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

    # Save image
    image.save(image_path)


if __name__ == '__main__':
    embed_text_in_rectangle("../images/test/_cropped/3677828385123675111.png", "acrylic on canvas painting of a quiet street corner, 3D relief painting texture, snowy dusk, dappled lighting, highly detailed, extremely intricate, meticulous painting, octane render, unreal engine, dramatic lighting, post processing")