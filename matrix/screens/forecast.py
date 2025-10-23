import os
from typing import TypedDict
import requests
import datetime

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, bigfont, smallfont
from matrix.screens.screen import REQUEST_DEFAULT_TIMEOUT, Screen


TIME_DATE_COLOR = "#aaaaaa"
HIGH_COLOR = "#ffa024"
LOW_COLOR = "#5cc9ff"


def k_to_f(k: float) -> float:
    return (k - 273.15) * 9 / 5 + 32


def k_to_c(k: float) -> float:
    return k - 273.15


class WeatherPrediction(TypedDict):
    id: int
    icon: str


class ForecastType(TypedDict):
    dt: int
    main: dict[str, float]
    weather: list[WeatherPrediction]


class WeatherData(TypedDict):
    list: list[ForecastType]


class Forecast(Screen[WeatherData | None]):
    CACHE_TTL = 600

    def fetch_data(self):
        weather_api_key = self.config["api_key"]
        weather_base_url = "https://api.openweathermap.org/data/2.5/forecast?"
        zip_code = self.config["zip_code"]

        weather_url = weather_base_url + "appid=" + weather_api_key + "&zip=" + zip_code

        return requests.get(weather_url, timeout=REQUEST_DEFAULT_TIMEOUT).json()

    def fallback_data(self):
        return None

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        date_str = datetime.datetime.now().strftime("%m/%d")
        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((1, 1), f"{date_str:<5}", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 1), f"{time_str:>5}", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        data = self.data

        dates: dict[datetime.date, list[ForecastType]] = {}

        for forecast in data["list"]:
            timestamp = datetime.datetime.fromtimestamp(
                forecast["dt"], tz=datetime.timezone.utc
            )

            if timestamp.date() not in dates:
                dates[timestamp.date()] = []
            dates[timestamp.date()].append(forecast)

        for i, (date, forecasts) in enumerate(
            sorted(dates.items(), key=lambda pair: pair[0])
        ):
            draw.text(
                (1, 10 + i * 10),
                date.strftime("%a") + " " + forecasts[0]["weather"][0]["description"],
                font=smallfont,
                fill="#ffffff",
            )

        return image

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        date_str = datetime.datetime.now().strftime("%m/%d")
        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((1, 1), f"{date_str:<5}", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 1), f"{time_str:>5}", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        data = self.data

        dates: dict[datetime.date, list[ForecastType]] = {}

        for forecast in data["list"]:
            timestamp = datetime.datetime.fromtimestamp(
                forecast["dt"], tz=datetime.timezone.utc
            )

            if timestamp.date() not in dates:
                dates[timestamp.date()] = []
            dates[timestamp.date()].append(forecast)

        for i, (date, forecasts) in enumerate(
            sorted(dates.items(), key=lambda pair: pair[0])
        ):
            draw.text(
                (1, 10 + i * 10),
                date.strftime("%a") + " " + forecasts[0]["weather"][0]["description"],
                font=smallfont,
                fill="#ffffff",
            )

        return image
