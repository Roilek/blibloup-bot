import io

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 512, 512
MIN_FONT_SIZE, MAX_FONT_SIZE = 1, 1000


def gen_sticker(text, font_name, color) -> Image:
    """Generate a sticker from a text, a font, and a text color."""
    font_size = MAX_FONT_SIZE
    # Binary search to find maximum font size that fits the width
    for line in text.splitlines():
        min_font_size, max_font_size = MIN_FONT_SIZE, font_size
        while max_font_size - min_font_size > 1:
            font_size = (min_font_size + max_font_size) // 2
            font = ImageFont.truetype(font_name, font_size)
            text_width, text_height = font.getsize(line)
            if text_width > WIDTH:
                max_font_size = font_size
            else:
                min_font_size = font_size

    # Binary search to find maximum font size that fits the height
    min_font_size, max_font_size = MIN_FONT_SIZE, font_size
    while max_font_size - min_font_size > 1:
        font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_name, font_size)
        text_width, text_height = font.getsize_multiline(text)
        if text_height > HEIGHT:
            max_font_size = font_size
        else:
            min_font_size = font_size

    # Create image
    img = Image.new('RGBA', (WIDTH, HEIGHT), color=(0, 0, 0, 0))
    # Load font
    font = ImageFont.truetype(font_name, font_size)
    # Draw text
    draw = ImageDraw.Draw(img)

    # Get text size
    text_width, text_height = draw.textsize(text, font)
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2
    draw.text((x, y), text, font=font, fill=color, align="center")

    # Convert to bytes
    with io.BytesIO() as bio:
        img.save(bio, format='PNG')
        bio.seek(0)
        image_bytes = bio.read()

    # Return image
    return image_bytes


def gen_sticker_agep(text) -> Image:
    """Generate a sticker from a text, using the agepoly font."""
    return gen_sticker(text, "agepoly.ttf", (227, 5, 19))


def test_gen_sticker() -> None:
    """Test the sticker generation and save it."""
    gen_sticker_agep("AGEPOLY").save("image.png")
    return


# Run tests if this file is run directly
if __name__ == '__main__':
    test_gen_sticker()
