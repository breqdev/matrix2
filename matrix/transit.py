from matrix.mbta import get_predictions

import requests
import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font


def get_image_transit(page: int) -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    heath_predictions = [
        ("Heath St", "#00ff76", *time)
        for time in get_predictions("place-mgngl", "Green-E", 0)
    ]
    medfd_predictions = [
        ("Medfd/Tu", "#00ff76", *time)
        for time in get_predictions("place-mgngl", "Green-E", 1)
    ]
    sullivan_predictions = [
        ("Sullivan", "#FFAA00", *time) for time in get_predictions("2698", "89", 1)
    ]
    davis_predictions = [
        ("Davis", "#FFAA00", *time) for time in get_predictions("2735", "89", 0)
    ]
    arlington_predictions = [
        ("Arlingtn", "#FFAA00", *time) for time in get_predictions("2735", "80", 0)
    ]
    lechmere_predictions = [
        ("Lechmere", "#FFAA00", *time) for time in get_predictions("2698", "80", 1)
    ]

    time_str = datetime.datetime.now().strftime("%H:%M")
    draw.text((1, 1), f"{page+1}/2", font=font, fill="#ffffff")
    draw.text((39, 1), f"{time_str:>5}", font=font, fill="#ffffff")

    predictions = [
        *heath_predictions,
        *medfd_predictions,
        *sullivan_predictions,
        *davis_predictions,
        *arlington_predictions,
        *lechmere_predictions,
    ]

    predictions_section = list(sorted(predictions, key=lambda p: p[2]))[
        page * 4 : page * 4 + 4
    ]

    for i, (label, color, wait, source) in list(enumerate(predictions_section)):
        time_str = str(int(wait / datetime.timedelta(minutes=1)))
        if source == "schedule":
            # show scheduled trips in gray to disambiguate
            color = "#888888"
        draw.text((1, 11 + 9 * i), f"{label:<8}", font=font, fill=color)
        draw.text((47, 11 + 9 * i), f"{time_str:>2}", font=font, fill=color)
        draw.text((59, 11 + 9 * i), "m", font=font, fill=color)

    STATIONS = {
        "S32022": "Cedar St",
        "S32013": "Trum Field",
        # "S32040": "Lowell St",
    }

    all_stations = requests.get(
        "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json"
    ).json()

    guids = {}
    for sta_id in STATIONS:
        sta_info = next(
            s for s in all_stations["data"]["stations"] if s["short_name"] == sta_id
        )
        guids[sta_id] = sta_info["station_id"]

    all_status = requests.get(
        "https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json"
    ).json()

    status = {}
    for sta_id in STATIONS:
        sta_status = next(
            s
            for s in all_status["data"]["stations"]
            if s["station_id"] == guids[sta_id]
        )
        status[sta_id] = sta_status

    sta_id, info = list(status.items())[page]

    draw.text((1, 48), text=STATIONS[sta_id], font=font, fill="#999999")
    image.paste(Image.open("icons/bike.png"), (1, 56))
    draw.text(
        (12, 57),
        text=f"{info['num_bikes_available']:0>2}",
        font=font,
        fill="#2CA3E1",
    )
    image.paste(Image.open("icons/ebike.png"), (25, 56))
    draw.text(
        (31, 57),
        text=f"{info['num_ebikes_available']:0>2}",
        font=font,
        fill="#b6d3d4",
    )
    image.paste(Image.open("icons/parking.png"), (45, 56))
    draw.text(
        (53, 57),
        text=f"{info['num_docks_available']:0>2}",
        font=font,
        fill="#4254f5",
    )

    return image
