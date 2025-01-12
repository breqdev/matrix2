import os
import requests
import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font

API_KEY = os.environ["MBTA_TOKEN"]

def get_predictions(origin: str, route: str, direction: int) -> list[datetime.timedelta]:
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

    current_time = datetime.datetime.now()

    realtime_times: list[datetime.timedelta] = []

    # Pull from realtime predictions first
    realtime_trips = set()

    for prediction in predictions:
        if len(realtime_times) >= 2:
            break

        trip_id = prediction["relationships"]["trip"]["data"]["id"]

        departure_time = prediction["attributes"]["departure_time"]
        if departure_time is None:
            continue

        realtime_trips.add(trip_id)
        departure_time = datetime.datetime.strptime(
            departure_time, "%Y-%m-%dT%H:%M:%S%z"
        )

        departure_time = departure_time.replace(tzinfo=None)
        wait_time = departure_time - current_time

        if wait_time <= datetime.timedelta(minutes=0):
            continue
        if wait_time >= datetime.timedelta(minutes=100):
            continue

        realtime_times.append(wait_time)

    if len(realtime_times) >= 2:
        return realtime_times


    # Handle mapping the current date/time to the service date/time
    # The current date/time and service date/time are the same UNLESS
    # it is between midnight and 3 AM, in which case the date is _yesterday_
    # and the time is 24 + (actual hour).
    # For instance, 1 AM on 9/2/24 is considered "25:00" on 9/1/24.

    # We have to rawdog the date representation here bc datetime, quite
    # rationally, won't represent hours above 24 for us

    wall_time = datetime.datetime.now().replace(tzinfo=None)

    if wall_time.hour < 3:
        service_date = wall_time.date() - datetime.timedelta(days=1)
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
            "filter[max_time]": f"{service_hour+2:02}:{service_minute:02}",
            "api_key": API_KEY,
        },
    )

    schedule_response.raise_for_status()

    schedules = schedule_response.json()["data"]

    # Then, pull from schedules
    scheduled_times: list[datetime.timedelta] = []
    for schedule in schedules:
        if len(realtime_times) + len(scheduled_times) >= 2:
            break

        trip_id = schedule["relationships"]["trip"]["data"]["id"]
        if trip_id in realtime_trips:
            continue

        departure_time = schedule["attributes"]["departure_time"]
        if departure_time is None:
            continue
        departure_time = datetime.datetime.strptime(
            departure_time, "%Y-%m-%dT%H:%M:%S%z"
        )

        departure_time = departure_time.replace(tzinfo=None)
        wait_time = departure_time - current_time

        if wait_time <= datetime.timedelta(minutes=0):
            continue
        if wait_time >= datetime.timedelta(minutes=100):
            continue

        scheduled_times.append(wait_time)

    return [*realtime_times, *scheduled_times]

def get_image_mbta() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    heath_predictions = [("Heath St", "#00ff76", time) for time in get_predictions("place-mgngl", "Green-E", 0)]
    medfd_predictions = [("Medfd/Tu", "#00ff76", time) for time in get_predictions("place-mgngl", "Green-E", 1)]
    sullivan_predictions = [("Sullivan", "#FFAA00", time) for time in get_predictions("2698", "89", 1)]
    davis_predictions = [("Davis", "#FFAA00", time) for time in get_predictions("2735", "89", 0)]
    arlington_predictions = [("Arlingtn", "#FFAA00", time) for time in get_predictions("2735", "80", 0)]
    lechmere_predictions = [("Lechmere", "#FFAA00", time) for time in get_predictions("2698", "80", 1)]

    time_str = datetime.datetime.now().strftime("%H:%M")
    draw.text((0, 1), f"MBTA    {time_str:>5}", font=font, fill="#FFAA00")

    predictions = [*heath_predictions, *medfd_predictions, *sullivan_predictions, *davis_predictions, *arlington_predictions, *lechmere_predictions]
    predictions.sort(key=lambda x: x[2])

    for i, (label, color, wait) in list(enumerate(predictions))[:6]:
        time_str = str(int(wait / datetime.timedelta(minutes=1)))
        draw.text((0, 12 + 9 * i), f"{label:<8} {time_str:>2} m", font=font, fill=color)

    return image
