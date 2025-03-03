import os
import requests
from datetime import datetime, timedelta
from typing import Literal, TypeAlias
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw

from matrix.utils.cache import DEFAULT_IMAGE_TTL, ttl_cache
from matrix.resources.fonts import font
from matrix.utils.timed import timed

API_KEY = os.environ["MBTA_TOKEN"]

PredictionType: TypeAlias = Literal["prediction", "schedule"]


def get_predictions(
    origin: str, route: str, direction: int
) -> list[tuple[timedelta, PredictionType]]:
    predictions_response = requests.get(
        "https://api-v3.mbta.com/predictions",
        params={
            "filter[stop]": origin,
            "filter[route]": route,
            "filter[direction_id]": str(direction),
            "include": "stop",
            "sort": "arrival_time",
            "page[limit]": "3",
            "api_key": API_KEY,
        },
    )

    predictions_response.raise_for_status()

    predictions = predictions_response.json()["data"]

    current_time = datetime.now()

    results: list[tuple[timedelta, PredictionType]] = []

    # Pull from realtime predictions first
    realtime_trips = set()

    for prediction in predictions:
        if len(results) >= 2:
            break

        trip_id = prediction["relationships"]["trip"]["data"]["id"]

        departure_time = prediction["attributes"]["departure_time"]
        if departure_time is None:
            continue

        realtime_trips.add(trip_id)
        departure_time = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")

        departure_time = departure_time.replace(tzinfo=None)
        wait_time = departure_time - current_time

        if wait_time <= timedelta(minutes=0):
            continue
        if wait_time >= timedelta(minutes=100):
            continue

        results.append((wait_time, "prediction"))

    if len(results) >= 2:
        return results

    # Handle mapping the current date/time to the service date/time
    # The current date/time and service date/time are the same UNLESS
    # it is between midnight and 3 AM, in which case the date is _yesterday_
    # and the time is 24 + (actual hour).
    # For instance, 1 AM on 9/2/24 is considered "25:00" on 9/1/24.

    # We have to rawdog the date representation here bc datetime, quite
    # rationally, won't represent hours above 24 for us

    wall_time = datetime.now().replace(tzinfo=None)

    if wall_time.hour < 3:
        service_date = wall_time.date() - timedelta(days=1)
        service_hour = wall_time.hour + 24
        service_minute = wall_time.minute
    else:
        service_date = wall_time.date()
        service_hour = wall_time.hour
        service_minute = wall_time.minute

    schedule_response = requests.get(
        "https://api-v3.mbta.com/schedules",
        params={
            "filter[stop]": origin,
            "filter[route]": route,
            "filter[direction_id]": str(direction),
            "include": "stop",
            "sort": "arrival_time",
            "page[limit]": "3",
            "filter[date]": service_date.strftime("%Y-%m-%d"),
            "filter[min_time]": f"{service_hour:02}:{service_minute:02}",
            "filter[max_time]": f"{service_hour + 2:02}:{service_minute:02}",
            "api_key": API_KEY,
        },
    )

    schedule_response.raise_for_status()

    schedules = schedule_response.json()["data"]

    # Then, pull from schedules
    for schedule in schedules:
        if len(results) >= 2:
            break

        trip_id = schedule["relationships"]["trip"]["data"]["id"]
        if trip_id in realtime_trips:
            continue

        departure_time = schedule["attributes"]["departure_time"]
        if departure_time is None:
            continue
        departure_time = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S%z")

        departure_time = departure_time.replace(tzinfo=None)
        wait_time = departure_time - current_time

        if wait_time <= timedelta(minutes=0):
            continue
        if wait_time >= timedelta(minutes=100):
            continue

        results.append((wait_time, "schedule"))

    return results


LINE_AND_COLOR_TO_ARGS = {
    ("Heath St", "#00ff76"): ("place-mgngl", "Green-E", 0),
    ("Medfd/Tu", "#00ff76"): ("place-mgngl", "Green-E", 1),
    ("Sullivan", "#FFAA00"): ("2698", "89", 1),
    ("Davis", "#FFAA00"): ("2735", "89", 0),
    ("Arlingtn", "#FFAA00"): ("2735", "80", 0),
    ("Lechmere", "#FFAA00"): ("2698", "80", 1),
}


@ttl_cache(seconds=31)
@timed("mbta")
def get_all_predictions() -> list[tuple[str, str, timedelta, PredictionType]]:
    with ThreadPoolExecutor() as tpe:
        predictions = [
            (line, color, *time)
            for (line, color), times in zip(
                LINE_AND_COLOR_TO_ARGS,
                tpe.map(
                    lambda args: get_predictions(*args), LINE_AND_COLOR_TO_ARGS.values()
                ),
            )
            for time in times
        ]
    predictions.sort(key=lambda x: x[2])
    return predictions


@ttl_cache(seconds=DEFAULT_IMAGE_TTL)
def get_image_mbta() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)
    predictions = get_all_predictions()
    time_str = datetime.now().strftime("%H:%M")
    draw.text((1, 1), "MBTA", font=font, fill="#FFAA00")
    draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

    if len(predictions) == 0:
        image.paste(Image.open("icons/train_sleeping.png"), (16, 11))

        draw.text((7, 45), "trains are", font=font, fill="#FFAA00")
        draw.text((7, 54), " sleeping", font=font, fill="#FFAA00")

        return image

    for i, (label, color, wait, source) in list(enumerate(predictions))[:6]:
        time_str = str(int(wait / timedelta(minutes=1)))
        if source == "schedule":
            # show scheduled trips in gray to disambiguate
            color = "#888888"
        draw.text((1, 12 + 9 * i), f"{label:<8}", font=font, fill=color)
        draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill=color)
        draw.text((59, 12 + 9 * i), "m", font=font, fill=color)

    # TODO: diversions, something like
    # draw.text((1, 40), "No Green Line", font=smallfont, fill="#ff0000")
    # draw.text((1, 46), "from Medfd/Tufts", font=smallfont, fill="#ff0000")
    # draw.text((1, 52), "to North Station", font=smallfont, fill="#ff0000")
    # draw.text((1, 58), "Use Shuttle Bus", font=smallfont, fill="#ff0000")

    return image
