import datetime
from pathlib import Path
from typing import TypedDict

from PIL import Image, ImageDraw

from matrix.resources.fonts import bigfont, font
from matrix.screens.screen import Screen
from matrix.utils.config import get_config

TIME_DATE_COLOR = "#aaaaaa"
HIGH_COLOR = "#ffa024"
LOW_COLOR = "#5cc9ff"


def c_to_f(c: float) -> float:
    return c * 9 / 5 + 32


class CurrentWeather(TypedDict):
    temperature_2m: float
    apparent_temperature: float
    weather_code: int
    is_day: int  # 1 = day, 0 = night


class DailyWeather(TypedDict):
    temperature_2m_max: list[float]
    temperature_2m_min: list[float]


class WeatherData(TypedDict):
    current: CurrentWeather
    daily: DailyWeather


# Maps icon name -> (daytime WMO codes, nighttime WMO codes)
WMO_ICON_MAP: dict[str, tuple[list[int], list[int]]] = {
    "sun": ([0], []),
    "moon": ([], [0]),
    "cloud_sun": ([1, 2], []),
    "cloud_moon": ([], [1, 2]),
    "cloud": ([3], [3]),
    "cloud_wind": ([45, 48], [45, 48]),
    "rain0_sun": ([51, 53], []),
    "rain0_moon": ([], [51, 53]),
    "rain0": ([55, 56, 57], [55, 56, 57]),
    "rain1_sun": ([61, 63], []),
    "rain1_moon": ([], [61, 63]),
    "rain1": ([65, 66, 67], [65, 66, 67]),
    "rain2": ([80, 81, 82], [80, 81, 82]),
    "rain_snow": ([68, 69], [68, 69]),
    "snow_sun": ([71, 73], []),
    "snow_moon": ([], [71, 73]),
    "snow": ([75, 77, 85, 86], [75, 77, 85, 86]),
    "rain_lightning": ([95, 96, 99], [95, 96, 99]),
}


def get_icon(wmo_code: int, is_day: bool) -> str | None:
    for icon, (day_codes, night_codes) in WMO_ICON_MAP.items():
        codes = day_codes if is_day else night_codes
        if wmo_code in codes:
            return icon
    return None


class Weather(Screen[WeatherData | None]):
    CACHE_TTL = 600

    def fetch_data(self):
        config = get_config().screens.weather
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={config.latitude}&longitude={config.longitude}"
            "&current=temperature_2m,apparent_temperature,"
            "weather_code,is_day"
            "&daily=temperature_2m_max,temperature_2m_min"
            "&temperature_unit=celsius"
            "&forecast_days=1"
            "&timezone=auto"
        )

        return self.fetch_url(url).json()

    def fallback_data(self):
        return None

    def get_image_64x64(self) -> Image.Image:
        image = Image.new("RGB", (64, 64))
        draw = ImageDraw.Draw(image)

        date_str = datetime.datetime.now().strftime("%m/%d")
        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((1, 1), f"{date_str:<5}", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 1), f"{time_str:>5}", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        data = self.data

        temp: float = data["current"]["temperature_2m"]
        temp_f = int(c_to_f(temp))
        temp_c = int(temp)

        temp_min: float = data["daily"]["temperature_2m_min"][0]
        temp_min_f = int(c_to_f(temp_min))
        temp_min_c = int(temp_min)

        temp_max: float = data["daily"]["temperature_2m_max"][0]
        temp_max_f = int(c_to_f(temp_max))
        temp_max_c = int(temp_max)

        icon_name = get_icon(data["current"]["weather_code"], bool(data["current"]["is_day"]))

        icon = Image.open(Path.cwd() / "icons" / "weather" / "32px" / f"{icon_name}.png")

        image.paste(icon, (1, 11))
        draw.text((39, 14), f"{temp_f:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 19), "F", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 28), f"{temp_c:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 33), "C", font=font, fill=TIME_DATE_COLOR)

        draw.line((4, 51, 6, 49, 8, 51), fill=HIGH_COLOR)
        draw.text((14, 47), f"{temp_max_f:>2}°F", font=font, fill=HIGH_COLOR)
        draw.text((40, 47), f"{temp_max_c:>2}°C", font=font, fill=HIGH_COLOR)
        draw.line((4, 57, 6, 59, 8, 57), fill=LOW_COLOR)
        draw.text((14, 55), f"{temp_min_f:>2}°F", font=font, fill=LOW_COLOR)
        draw.text((40, 55), f"{temp_min_c:>2}°C", font=font, fill=LOW_COLOR)

        return image

    def get_image_64x32(self) -> Image.Image:
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((39, 24), f"{time_str:>5}", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        data = self.data

        temp: float = data["current"]["temperature_2m"]
        temp_f = int(c_to_f(temp))
        temp_c = int(temp)

        icon_name = get_icon(data["current"]["weather_code"], bool(data["current"]["is_day"]))

        icon = Image.open(Path.cwd() / "icons" / "weather" / "32px" / f"{icon_name}.png")

        image.paste(icon, (1, 0))
        draw.text((39, 0), f"{temp_f:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 5), "F", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 11), f"{temp_c:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 16), "C", font=font, fill=TIME_DATE_COLOR)

        return image
