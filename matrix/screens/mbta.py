import requests
from datetime import datetime, timedelta
from typing import Literal, TypeAlias
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import re

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, smallfont
from matrix.screens.screen import Screen, REQUEST_DEFAULT_TIMEOUT

PredictionType: TypeAlias = Literal["prediction", "schedule"]


@dataclass
class Line:
    symbol: str
    headsign: str
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


def get_predictions(line: Line, api_key: str) -> list[Prediction]:
    predictions_response = requests.get(
        "https://api-v3.mbta.com/predictions",
        params={
            "filter[stop]": line.stop_id,
            "filter[route]": line.route_id,
            "filter[direction_id]": str(line.direction_id),
            "include": "stop",
            "sort": "arrival_time",
            "page[limit]": "10",
            "api_key": api_key,
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
            "api_key": api_key,
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


def get_alert(line: Line, api_key: str) -> str | None:
    response = requests.get(
        "https://api-v3.mbta.com/alerts",
        params={
            "filter[route]": line.route_id,
            "filter[datetime]": "NOW",
            "api_key": api_key,
        },
        timeout=REQUEST_DEFAULT_TIMEOUT,
    )

    response.raise_for_status()
    data = response.json()["data"]

    if len(data) == 0:
        return None

    mbta_text = data[0]["attributes"]["short_header"]

    # Bus alerts of the form
    # Route 109 is experiencing delays of up to 20 minutes due to traffic
    # can be condensed

    pattern = r"Route\s+(\d+)\s+is experiencing delays of up to (\d+)\s+minutes(?:\s+due to\s+(.*))?$"
    match = re.search(pattern, mbta_text, re.IGNORECASE)
    if match:
        if match.group(3):
            # 20 minute delay (traffic)
            # 15 minute delay (disabled bus)
            return f"{match.group(2)}min delay ({match.group(3)})"
        else:
            return f"{match.group(2)}min delay"

    # The part of the message before the colon can be removed
    # Example:
    # Green Line E branch: Delays of about 20 minutes due to a disabled auto blocking the tracks near Mission Park.
    if ": " in mbta_text:
        prefix, message = mbta_text.split(": ")
        mbta_text = message

    # If this alert is multiple sentences, only return the first one
    # Example:
    # Delays of about 15 minutes due to a disabled train at Back Bay. Trains may stand by at stations.
    if ". " in mbta_text:
        mbta_text = mbta_text.split(". ")[0]

    # If it starts with "Delays of about X minutes due to a", replace with "Xmin delay:"
    pattern = r"^Delays of about (\d+) minutes due to (?:a )?(.*)"
    match = re.match(pattern, mbta_text, re.IGNORECASE)
    if match:
        minutes, reason = match.groups()
        return f"{minutes}min delay: {reason}"

    return mbta_text


MbtaData: TypeAlias = tuple[list[Prediction], str | None, Line | None]


def darken_hex(color: str):
    r, g, b = (int(color.lstrip("#")[i * 2 : i * 2 + 2], 16) for i in range(3))
    x = 0.5
    return f"#{int(r * x):02x}{int(g * x):02x}{int(b * x):02x}"


class MBTA(Screen[MbtaData]):
    CACHE_TTL = 30

    def __init__(self, config: dict):
        self.scroll_idx = 0

        self.lines = []
        for item in config["lines"]:
            self.lines.append(
                Line(
                    symbol=item["symbol"],
                    headsign=item["headsign"],
                    label=item["label"],
                    color=item["color"],
                    stop_id=item["stop_id"],
                    route_id=item["route_id"],
                    direction_id=item["direction_id"],
                )
            )

        super().__init__(config)

    def fetch_data(self):
        api_key = self.config["api_key"]

        with ThreadPoolExecutor() as tpe:
            predictions = [
                prediction
                for line_predictions in tpe.map(
                    lambda line: get_predictions(line, api_key),
                    self.lines,
                )
                for prediction in line_predictions
            ]
        predictions.sort(key=lambda x: x.eta)

        alert = None
        alert_line = None
        for line in self.lines[:2]:
            alert = get_alert(line, api_key)
            if alert is not None:
                alert_line = line
                break

        return (predictions, alert, alert_line)

    def fallback_data(self):
        return ([], None, None)

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)
        predictions, alert, alert_line = self.data
        time_str = datetime.now().strftime("%H:%M")
        draw.text((1, 1), "Transit", font=font, fill="#FFAA00")
        draw.text((39, 1), f"{time_str:>5}", font=font, fill="#FFAA00")

        if len(predictions) == 0:
            image.paste(Image.open("icons/train_sleeping.png"), (16, 11))

            draw.text((7, 45), "trains are", font=font, fill="#FFAA00")
            draw.text((7, 54), " sleeping", font=font, fill="#FFAA00")

            return image

        X_MARGIN = 3

        lines_displayed = 2 if alert else 3

        for row, line in enumerate(self.lines[:lines_displayed]):
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

            draw.text((6 + length, 10 + 19 * row), line.headsign, font=font, fill=line.color)
            line_predictions = filter(lambda p: p.line == line, predictions)

            pixel_x = 2
            for col, prediction in enumerate(line_predictions):
                time_str = str(int(prediction.eta / timedelta(minutes=1)))
                length = draw.textlength(time_str, font=font)
                if pixel_x + length > 64 - (draw.textlength("min", font=font) + X_MARGIN):
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

        if alert:
            alert_text = alert + "  "
            textlength = draw.textlength(alert_text, font=font)

            image.paste(Image.open("icons/alert.png"), (1, 46))

            draw.line((9, 47, 60, 47), fill="#888888")

            draw.text((12, 50), f"{alert_line.label} Alert", font=smallfont, fill="#888888")

            draw.text((1 - self.scroll_idx, 57), alert_text, font=font, fill="#ff0000")
            draw.text(
                (1 - self.scroll_idx + textlength, 57),
                alert_text,
                font=font,
                fill="#ff0000",
            )
            self.scroll_idx += 1
            self.scroll_idx %= textlength

        return image

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)
        predictions, alert, alert_line = self.data

        if len(predictions) == 0:
            image.paste(Image.open("icons/train_sleeping.png"), (16, 0))

            return image

        X_MARGIN = 3

        lines_displayed = 2

        for row, line in enumerate(self.lines[:lines_displayed]):
            length = draw.textlength(line.symbol, font=font)

            draw.rectangle(
                (1, 1 + 16 * row, 1 + length + 2, 10 + 16 * row),
                outline=darken_hex(line.color),
            )
            draw.point((1, 1 + 16 * row), fill="#000000")
            draw.point((1, 10 + 16 * row), fill="#000000")
            draw.point((1 + length + 2, 1 + 16 * row), fill="#000000")
            draw.point((1 + length + 2, 10 + 16 * row), fill="#000000")

            draw.text((3, 3 + 16 * row), line.symbol, font=font, fill=line.color)

            draw.text(
                (6 + length, 1 + 16 * row),
                line.headsign,
                font=smallfont,
                fill=line.color,
            )
            line_predictions = filter(lambda p: p.line == line, predictions)

            pixel_x = 1 + length + 2 + 3
            for col, prediction in enumerate(line_predictions):
                time_str = str(int(prediction.eta / timedelta(minutes=1)))
                length = draw.textlength(time_str, font=font)
                if pixel_x + length > 64 - (draw.textlength("min", font=font) + X_MARGIN):
                    break

                draw.text(
                    (pixel_x, 8 + 16 * row),
                    time_str,
                    font=font,
                    fill=line.color if prediction.type == "prediction" else "#888888",
                )

                pixel_x += length + X_MARGIN

            draw.text(
                (pixel_x, 8 + 16 * row),
                "min",
                font=font,
                fill="#888888",
            )

        return image

    def get_time_stretch(self):
        if self.data:
            if self.data[1]:
                # remain on screen for 5s for alerts
                return 10
