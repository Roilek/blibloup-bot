import io

from PIL import Image, ImageDraw, ImageFont


def gen_sticker(text, font_name, color, background_color) -> Image:
    # Créer une nouvelle image de taille 512x512
    width, height = 512, 512
    img = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))

    # Charger la police ISOCPEUR
    font = ImageFont.truetype(font_name)

    # Créer un objet ImageDraw pour dessiner sur l'image
    draw = ImageDraw.Draw(img)

    # Binary search to find maximum font size that fits in image
    min_font_size, max_font_size = 1, 1000
    while max_font_size - min_font_size > 1:
        font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_name, font_size)
        text_width, text_height = font.getsize(text)
        if text_width > width or text_height > height:
            max_font_size = font_size
        else:
            min_font_size = font_size

    # Dessiner le texte centré sur l'image
    textwidth, textheight = draw.textsize(text, font)
    x = (512 - textwidth) / 2
    y = (512 - textheight) / 2
    draw.text((x, y), text, font=font, fill=color, align="center")

    with io.BytesIO() as bio:
        img.save(bio, format='PNG')
        bio.seek(0)
        image_bytes = bio.read()

    # Retourner l'image sous un format utilisable par Telegram
    return image_bytes


def gen_sticker_agep(text) -> Image:
    return gen_sticker(text, "agepoly.ttf", (227, 5, 19), "blank")


def test_gen_sticker() -> None:
    gen_sticker_agep("Agepoulay").save("image.png")
    return


if __name__ == '__main__':
    test_gen_sticker()
