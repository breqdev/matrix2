import datetime
from pathlib import Path
from typing import TypedDict

import requests
from PIL import Image, ImageDraw

from matrix.resources.fonts import font
from matrix.screens.screen import Screen
from matrix.screens.weather import (
    HIGH_COLOR,
    LOW_COLOR,
    TIME_DATE_COLOR,
    c_to_f,
    get_icon,
)

PRECIP_COLOR = "#58a8f0"


class DailyForecast(TypedDict):
    time: list[str]
    weather_code: list[int]
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]
    precipitation_probability_max: list[int]


class ForecastData(TypedDict):
    daily: DailyForecast


class Forecast(Screen[ForecastData | None]):
    CACHE_TTL = 1200

    def fetch_data(self):
        lat = self.config["latitude"]
        lon = self.config["longitude"]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&daily=weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max"
            "&temperature_unit=celsius"
            "&forecast_days=4"
            "&timezone=auto"
        )

        return self.fetch_url(url).json()

    def fallback_data(self):
        return None

    def get_image_64x64(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        # Top bar
        draw.text((1, 1), "Forecast", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        daily = self.data["daily"]

        # Indices 1-3 skip today
        for i, day_index in enumerate([1, 2, 3]):
            y = 10 + i * 18

            date_str = daily["time"][day_index]
            day_label = datetime.date.fromisoformat(date_str).strftime("%a").title()

            temp_max_f = int(c_to_f(daily["temperature_2m_max"][day_index]))
            temp_min_f = int(c_to_f(daily["temperature_2m_min"][day_index]))
            precip = daily["precipitation_probability_max"][day_index]

            draw.text((1, y), day_label, font=font, fill=TIME_DATE_COLOR)

            precip_icon = Image.open(
                Path.cwd()
                / "icons"
                / "weather"
                / "precip"
                / f"{int(round(precip / 100 * 5)) * 20}.png"
            )
            image.paste(precip_icon, (0, y + 8))

            draw.text((7, y + 9), f"{precip:>2}%", font=font, fill=PRECIP_COLOR)

            wmo_code = daily["weather_code"][day_index]
            icon_name = get_icon(wmo_code, is_day=True)
            if icon_name is not None:
                icon = Image.open(
                    Path.cwd() / "icons" / "weather" / "16px" / f"{icon_name}.png"
                )
                image.paste(icon, (23, y))

            draw.line((42, y + 3, 44, y + 1, 46, y + 3), fill=HIGH_COLOR)
            draw.text((49, y), f"{temp_max_f}°", font=font, fill=HIGH_COLOR)
            draw.line((42, y + 11, 44, y + 13, 46, y + 11), fill=LOW_COLOR)
            draw.text((49, y + 9), f"{temp_min_f}°", font=font, fill=LOW_COLOR)

        return image
