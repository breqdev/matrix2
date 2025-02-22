import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font


def get_image_approaching() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    time_str = datetime.datetime.now().strftime("%H:%M")
    # draw.text((1, 1), "MBTA", font=font, fill="#FFAA00")
    draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

    for i, (label, wait) in list(
        enumerate(
            [
                ("dial a fish", datetime.timedelta(minutes=5)),
                ("make a fish", datetime.timedelta(minutes=5)),
                # "make a wiish", datetime.timedelta(minutes=5),
                ("ssh a fish", datetime.timedelta(minutes=5)),
                ("spin a fish", datetime.timedelta(minutes=5)),
                # "X11:11 a fish", datetime.timedelta(minutes=5),
                ("bake a dish", datetime.timedelta(minutes=5)),
                ("make a seq.", datetime.timedelta(minutes=5)),
            ]
        )
    ):
        time_str = str(int(wait / datetime.timedelta(minutes=1)))
        draw.text((1, 12 + 9 * i), f"{label:<8}", font=font, fill="#FFAA00")
        draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill="#FFAA00")
        draw.text((59, 12 + 9 * i), "m", font=font, fill="#FFAA00")

    # TODO: diversions, something like
    # draw.text((1, 40), "No Green Line", font=smallfont, fill="#ff0000")
    # draw.text((1, 46), "from Medfd/Tufts", font=smallfont, fill="#ff0000")
    # draw.text((1, 52), "to North Station", font=smallfont, fill="#ff0000")
    # draw.text((1, 58), "Use Shuttle Bus", font=smallfont, fill="#ff0000")

    return image
