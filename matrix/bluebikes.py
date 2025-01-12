import requests
import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font

def get_image_bluebikes() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    STATIONS = {
        "S32022": "Cedar St",
        "S32013": "Trum Field",
        "S32040": "Lowell St",
        # "S32007": "Ball Sq",
    }

    all_stations = requests.get("https://gbfs.lyft.com/gbfs/1.1/bos/en/station_information.json").json()

    guids = {}
    for sta_id in STATIONS:
        sta_info = next(s for s in all_stations["data"]["stations"] if s["short_name"] == sta_id)
        guids[sta_id] = sta_info["station_id"]

    all_status = requests.get("https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json").json()

    status = {}
    for sta_id in STATIONS:
        sta_status = next(s for s in all_status["data"]["stations"] if s["station_id"] == guids[sta_id])
        status[sta_id] = sta_status

    time_str = datetime.datetime.now().strftime("%H:%M")
    draw.text((0, 1), f"Bikes   {time_str:>5}", font=font, fill="#2CA3E1")

    for i, (sta_id, info) in enumerate(status.items()):
        draw.text((0, 10 + 18 * i), text=STATIONS[sta_id], font=font, fill="#999999")
        image.paste(Image.open("icons/bike.png"), (0, 18 + 18 * i))
        draw.text((11, 18 + 18 * i), text=f"{info['num_bikes_available']:0>2}", font=font, fill="#2CA3E1")
        image.paste(Image.open("icons/ebike.png"), (24, 18 + 18 * i))
        draw.text((30, 18 + 18 * i), text=f"{info['num_ebikes_available']:0>2}", font=font, fill="#b6d3d4")
        image.paste(Image.open("icons/parking.png"), (44, 18 + 18 * i))
        draw.text((52, 18 + 18 * i), text=f"{info['num_docks_available']:0>2}", font=font, fill="#4254f5")

    return image
