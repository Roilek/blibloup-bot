import io

from PIL import Image, ImageDraw, ImageFont


def gen_sticker(text, font_name, font_size, color, background_color) -> Image:
    # Créer une nouvelle image de taille 512x512
    img = Image.new('RGB', (512, 512), color=color)

    # Charger la police ISOCPEUR
    font = ImageFont.truetype(font_name, font_size)

    # Créer un objet ImageDraw pour dessiner sur l'image
    draw = ImageDraw.Draw(img)

    # Dessiner le texte centré sur l'image
    textwidth, textheight = draw.textsize(text, font)
    x = (512 - textwidth) / 2
    y = (512 - textheight) / 2
    draw.text((x, y), text, font=font)

    with io.BytesIO() as bio:
        img.save(bio, format='PNG')
        bio.seek(0)
        image_bytes = bio.read()

    # Retourner l'image sous un format utilisable par Telegram
    return image_bytes


def gen_sticker_agep(text) -> Image:
    return gen_sticker(text, "agepoly.ttf", 50, "red", "blank")


def test_gen_sticker() -> None:
    gen_sticker_agep("Agepoulay").save("image.png")
    return


if __name__ == '__main__':
    test_gen_sticker()
