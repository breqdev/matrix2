import os
import requests
from datetime import datetime, timedelta
from typing import Literal, TypeAlias
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import colorsys

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, smallfont
from matrix.screens.screen import Screen, REQUEST_DEFAULT_TIMEOUT

API_KEY = os.environ["MBTA_TOKEN"]

PredictionType: TypeAlias = Literal["prediction", "schedule"]


@dataclass
class Line:
    symbol: str
    label: str
    color: str
    stop_id: str
    route_id: str
    direction_id: int


@dataclass
class Prediction:
    line: Line
    eta: timedelta
    type: PredictionType


def get_predictions(line: Line) -> list[Prediction]:
    predictions_response = requests.get(
        "https://api-v3.mbta.com/predictions",
        params={
            "filter[stop]": line.stop_id,
            "filter[route]": line.route_id,
            "filter[direction_id]": str(line.direction_id),
            "include": "stop",
            "sort": "arrival_time",
            "page[limit]": "10",
            "api_key": API_KEY,
        },
        timeout=REQUEST_DEFAULT_TIMEOUT,
    )

    predictions_response.raise_for_status()

    predictions = predictions_response.json()["data"]

    current_time = datetime.now()

    results: list[Prediction] = []

    # Pull from realtime predictions first
    realtime_trips = set()

    for prediction in predictions:
        if len(results) >= 6:
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

        results.append(Prediction(line=line, eta=wait_time, type="prediction"))

    if len(results) >= 6:
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
            "filter[stop]": line.stop_id,
            "filter[route]": line.route_id,
            "filter[direction_id]": str(line.direction_id),
            "include": "stop",
            "sort": "arrival_time",
            "page[limit]": "10",
            "filter[date]": service_date.strftime("%Y-%m-%d"),
            "filter[min_time]": f"{service_hour:02}:{service_minute:02}",
            "filter[max_time]": f"{service_hour + 2:02}:{service_minute:02}",
            "api_key": API_KEY,
        },
        timeout=REQUEST_DEFAULT_TIMEOUT,
    )

    schedule_response.raise_for_status()

    schedules = schedule_response.json()["data"]

    # Then, pull from schedules
    for schedule in schedules:
        if len(results) >= 6:
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

        results.append(Prediction(line=line, eta=wait_time, type="schedule"))

    return results


LINES = [
    Line(
        symbol="E",
        label="Heath St",
        color="#00ff76",
        stop_id="place-mgngl",
        route_id="Green-E",
        direction_id=0,
    ),
    Line(
        symbol="E",
        label="Medfd/Tuft",
        color="#00ff76",
        stop_id="place-mgngl",
        route_id="Green-E",
        direction_id=1,
    ),
    Line(
        symbol="89",
        label="Sullivan",
        color="#FFAA00",
        stop_id="2698",
        route_id="89",
        direction_id=1,
    ),
    # Line(
    #     symbol="89",
    #     label="Davis",
    #     color="#FFAA00",
    #     stop_id="2735",
    #     route_id="89",
    #     direction_id=0,
    # ),
    # Line(
    #     symbol="80",
    #     label="Arlington",
    #     color="#FFAA00",
    #     stop_id="2735",
    #     route_id="80",
    #     direction_id=0,
    # ),
    # Line(
    #     symbol="80",
    #     label="Lechmere",
    #     color="#FFAA00",
    #     stop_id="2698",
    #     route_id="80",
    #     direction_id=1,
    # ),
]

MbtaData: TypeAlias = list[Prediction]


def darken_hex(color: str):
    r, g, b = (int(color.lstrip("#")[i + 1 : i + 3], 16) / 255 for i in range(3))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(h, s, v * 0.7)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


class MBTA(Screen[MbtaData]):
    CACHE_TTL = 30

    def fetch_data(self):
        with ThreadPoolExecutor() as tpe:
            predictions = [
                prediction
                for line_predictions in tpe.map(
                    lambda line: get_predictions(line), LINES
                )
                for prediction in line_predictions
            ]
        predictions.sort(key=lambda x: x.eta)
        return predictions

    def fallback_data(self):
        return []

    def get_image(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)
        predictions = self.data
        time_str = datetime.now().strftime("%H:%M")
        draw.text((1, 1), "MBTA", font=font, fill="#FFAA00")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

        if len(predictions) == 0:
            image.paste(Image.open("icons/train_sleeping.png"), (16, 11))

            draw.text((7, 45), "trains are", font=font, fill="#FFAA00")
            draw.text((7, 54), " sleeping", font=font, fill="#FFAA00")

            return image

        # for i, prediction in list(enumerate(predictions))[:6]:
        #     time_str = str(int(prediction.eta / timedelta(minutes=1)))

        #     if prediction.type == "schedule":
        #         # show scheduled trips in gray to disambiguate
        #         color = "#888888"
        #     else:
        #         color = prediction.line.color

        #     draw.text(
        #         (1, 12 + 9 * i), f"{prediction.line.label:<8}", font=font, fill=color
        #     )
        #     draw.text((47, 12 + 9 * i), f"{time_str:>2}", font=font, fill=color)
        #     draw.text((59, 12 + 9 * i), "m", font=font, fill=color)

        X_MARGIN = 3

        for row, line in enumerate(LINES):
            length = draw.textlength(line.symbol, font=smallfont)

            draw.rectangle(
                (1, 9 + 19 * row, 1 + length + 2, 17 + 19 * row),
                outline=darken_hex(line.color),
            )
            draw.point((1, 9 + 19 * row), fill="#000000")
            draw.point((1, 17 + 19 * row), fill="#000000")
            draw.point((1 + length + 2, 9 + 19 * row), fill="#000000")
            draw.point((1 + length + 2, 17 + 19 * row), fill="#000000")

            draw.text((3, 11 + 19 * row), line.symbol, font=smallfont, fill=line.color)

            draw.text(
                (6 + length, 10 + 19 * row), line.label, font=font, fill=line.color
            )
            line_predictions = filter(lambda p: p.line == line, predictions)

            pixel_x = 2
            for col, prediction in enumerate(line_predictions):
                time_str = str(int(prediction.eta / timedelta(minutes=1)))
                length = draw.textlength(time_str, font=font)
                if pixel_x + length > 64 - (
                    draw.textlength("min", font=font) + X_MARGIN
                ):
                    break

                draw.text(
                    (pixel_x, 19 + 19 * row),
                    time_str,
                    font=font,
                    fill=line.color if prediction.type == "prediction" else "#888888",
                )

                pixel_x += length + X_MARGIN

            draw.text(
                (pixel_x, 19 + 19 * row),
                "min",
                font=font,
                fill="#888888",
            )

        # TODO: diversions, something like
        # draw.text((1, 40), "No Green Line", font=smallfont, fill="#ff0000")
        # draw.text((1, 46), "from Medfd/Tufts", font=smallfont, fill="#ff0000")
        # draw.text((1, 52), "to North Station", font=smallfont, fill="#ff0000")
        # draw.text((1, 58), "Use Shuttle Bus", font=smallfont, fill="#ff0000")

        return image
