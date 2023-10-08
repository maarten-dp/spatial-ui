from pathlib import Path

from PIL import ImageFont

HERE = Path(__file__).parent
DEFAULT_FONT_PATH = (HERE / "DejaVuSans.ttf").as_posix()
DEFAULT_FONT = ImageFont.truetype(font=DEFAULT_FONT_PATH, size=6)

FONTS = {}


def get_font(font_family: str, size: int):
    key = (font_family, size)
    if key in FONTS:
        return FONTS[key]

    try:
        font = ImageFont.truetype(font=font_family, size=size)
    except OSError:
        print(f"font not found {font_family}")
        font = ImageFont.truetype(font=DEFAULT_FONT_PATH, size=size)

    FONTS[key] = font
    return font
