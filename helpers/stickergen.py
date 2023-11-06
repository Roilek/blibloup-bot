import io

from PIL import Image, ImageDraw, ImageFont

import math


WIDTH, HEIGHT = 512, 512
MAX_RADIUS = min(WIDTH, HEIGHT) * 0.85
MIN_FONT_SIZE, MAX_FONT_SIZE = 1, 1000
COEF_REDUCTION_CIRCLE = 0.6


def draw_text(draw: ImageDraw, text: str, font_name: str, font_size: int, color: (int, int, int), align: str = "center") -> ImageDraw:
    font = ImageFont.truetype(font_name, font_size)
    # Get text size
    text_width, text_height = draw.textsize(text, font)
    x = (WIDTH - text_width) / 2
    y = (HEIGHT - text_height) / 2
    draw.text((x, y), text, font=font, fill=color, align=align)
    return draw


def draw_circle(draw: ImageDraw, color: (int, int, int), radius: int = min(WIDTH, HEIGHT)) -> ImageDraw:
    draw.ellipse((0, 0, radius, radius), fill=color)
    return draw


def compute_font_size(text: str, font_name: str, max_size: int, min_size: int = MIN_FONT_SIZE, width: int = WIDTH, height: int = HEIGHT) -> int:
    while min_size < max_size - 1:
        mid_size = (max_size + min_size) // 2
        font = ImageFont.truetype(font_name, mid_size)
        if font.getsize_multiline(text)[0] > width or font.getsize_multiline(text)[1] > height:
            max_size = mid_size
        else:
            min_size = mid_size
    return min_size



def circle_width_at_height(h, k, r, y1):
    """Return the width of a circle at a given height."""
    if abs(y1 - k) > r:
        raise ValueError("The given height is outside the circle.")
    x_left = h - math.sqrt(r**2 - (y1-k)**2)
    x_right = h + math.sqrt(r**2 - (y1-k)**2)
    return x_right - x_left


def strong(text: str, font_name: str, max_size: int, min_size: int = MIN_FONT_SIZE):
    # if odd number of lines
    # size is ce qui rentre dans la width et pour qui la height est ok en fonction de la résolution de l'équation
    pass

def compute_font_size_circle(text: str, font_name: str, max_size: int, min_size: int = MIN_FONT_SIZE, width: int = WIDTH, height: int = HEIGHT) -> int:
    lines = text.split("\n")
    nb_lines = len(lines)
    for i in range(nb_lines):
        lines[i] = lines[i].strip()
    if nb_lines % 2 == 1:
        index_mid = int(nb_lines//2)
        max_size = min(max_size, compute_font_size(lines[index_mid], font_name, max_size))
        print(max_size)
        for i in range(1, index_mid+1, 1):
            font = ImageFont.truetype(font_name, max_size)
            height_text = font.getsize(lines[index_mid-i])[1]*i
            circle_width = circle_width_at_height(0, 0, WIDTH/2, height_text)
            max_size = min(max_size, compute_font_size(lines[index_mid-i], font_name, max_size, width=circle_width))
            max_size = min(max_size, compute_font_size(lines[index_mid+i], font_name, max_size, width=circle_width))
    else:
        pass
        index_mid = int(nb_lines//2)
        for i in range(index_mid):
            coef = 1 - i*COEF_REDUCTION_CIRCLE
            max_size = min(max_size, compute_font_size(lines[index_mid-i], font_name, int(max_size*coef)))
            max_size = min(max_size, compute_font_size(lines[index_mid+i], font_name, int(max_size*coef)))
    return max_size


def min_radius_for_text(text: str, font_name: str, max_radius) -> int:
    font = ImageFont.truetype(font_name, MAX_FONT_SIZE)
    left, top, right, bottom = font.getbbox("AAAAAAAAAAAAAAAAA")
    standard_height = bottom - top
    lines = text.split("\n")
    nb_lines = len(lines)
    min_radius = 0
    for i in range(nb_lines):
        left, top, right, bottom = font.getbbox(lines[i].strip())
        width = right - left
        height = bottom - top + (nb_lines % 2) * standard_height / 2 + ((nb_lines // 2) - i) * standard_height
        min_radius = max(min_radius, distance_between_points((0, 0), (width, height)))
    print(min_radius)
    font_size = MAX_FONT_SIZE * max_radius // min_radius
    return int(font_size)


def distance_between_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance


def get_bytes(img: Image):
    # Convert to bytes
    with io.BytesIO() as bio:
        img.save(bio, format='PNG')
        bio.seek(0)
        image_bytes = bio.read()

    # Return image
    return image_bytes


def sticker_text_only(text: str, font_name: str, color: (int, int, int) = (0, 0, 0)) -> Image:
    img = Image.new('RGBA', (WIDTH, HEIGHT), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_text(draw, text, font_name, compute_font_size(text, font_name, MAX_FONT_SIZE), color)
    return get_bytes(img)


def sticker_text_on_circle(text: str, font_name: str, circle_color: (int, int, int) = (0, 0, 0), text_color: (int, int, int) = (255, 255, 255)) -> Image:
    img = Image.new('RGBA', (WIDTH, HEIGHT), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw = draw_circle(draw, circle_color)
    draw_text(draw, text, font_name, min_radius_for_text(text, font_name, MAX_RADIUS), text_color)
    return get_bytes(img)


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
    return gen_sticker(text, "resources/fonts/agepoly.ttf", (227, 5, 19))


def test_gen_sticker() -> None:
    """Test the sticker generation and save it."""
    image_bytes = sticker_text_on_circle("THONTHONTHON\nTHONTHONTHON\nTHONTHONTHON\nTHONTHONTHON", "../resources/fonts/arial.ttf", (255, 165, 0), (0, 0, 0))
    with open("../resources/products/image-3.png", "wb") as f:
        f.write(image_bytes)
    return


def test() -> None:
    """Test the sticker generation and save it."""
    min_radius_for_text("Heu\nHeu\nHeu\nblblblblndjkewnw\nHeu\nHeu\nHeu", "../resources/fonts/arial.ttf")
    return


def test2() -> int:
    text = "AA"
    font_name = "../resources/fonts/arial.ttf"
    circle_color = (255, 165, 0)
    text_color = (0, 0, 0)
    font = ImageFont.truetype(font_name, MAX_FONT_SIZE)
    left, top, right, bottom = font.getbbox("AAAAAAAAAAAAAAAAA")
    standard_height = bottom - top
    lines = text.split("\n")
    nb_lines = len(lines)
    min_radius = 0
    for i in range(nb_lines):
        left, top, right, bottom = font.getbbox(lines[i].strip())
        width = right - left
        height = bottom - top + (nb_lines % 2) * standard_height / 2 + ((nb_lines // 2) - i) * standard_height
        min_radius = max(min_radius, distance_between_points((0, 0), (width, height)))
    print(min_radius)
    font_size = int(MAX_FONT_SIZE * MAX_FONT_SIZE // min_radius)
    img = Image.new('RGBA', (int(min_radius)*2, int(min_radius)*2), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw = draw_circle(draw, circle_color)
    draw_text(draw, text, font_name, MAX_FONT_SIZE, text_color)
    with open("../resources/products/image-4.png", "wb") as f:
        f.write(get_bytes(img))


# Run tests if this file is run directly
if __name__ == '__main__':
    #test_gen_sticker()
    #test()
    test2()
