from typing import TypedDict
import requests
import datetime
from pathlib import Path

from PIL import Image, ImageDraw

from matrix.resources.fonts import font, bigfont
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


class WeatherData(TypedDict):
    main: dict[str, float]
    weather: list[WeatherPrediction]


class Weather(Screen[WeatherData | None]):
    CACHE_TTL = 600

    def fetch_data(self):
        weather_api_key = self.config["api_key"]
        weather_base_url = "https://api.openweathermap.org/data/2.5/weather?"
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

        temp: float = data["main"]["temp"]
        temp_f = int(k_to_f(temp))
        temp_c = int(k_to_c(temp))

        temp_min: float = data["main"]["temp_min"]
        temp_min_f = int(k_to_f(temp_min))
        temp_min_c = int(k_to_c(temp_min))

        temp_max: float = data["main"]["temp_max"]
        temp_max_f = int(k_to_f(temp_max))
        temp_max_c = int(k_to_c(temp_max))

        DAYTIME: dict[str, list[int]] = {
            "cloud": [803],
            "cloud_moon": [],
            "cloud_sun": [801, 802],
            "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
            "cloud_wind_moon": [],
            "cloud_wind_sun": [701],
            "clouds": [804],
            "lightning": [210, 211, 212, 221],
            "moon": [],
            "rain0": [302, 310, 311, 312, 313, 314, 321],
            "rain0_sun": [300, 301],
            "rain1": [502, 521, 522],
            "rain1_moon": [],
            "rain1_sun": [500, 501],
            "rain2": [503, 504, 531],
            "rain_lightning": [200, 201, 202, 230, 231, 232],
            "rain_snow": [511, 615, 616],
            "snow": [602, 613, 621, 622],
            "snow_moon": [],
            "snow_sun": [600, 601, 611, 612, 620],
            "sun": [800],
            "wind": [771, 781],
        }

        NIGHTTIME: dict[str, list[int]] = {
            "cloud": [803],
            "cloud_moon": [801, 802],
            "cloud_sun": [],
            "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
            "cloud_wind_moon": [701],
            "cloud_wind_sun": [],
            "clouds": [804],
            "lightning": [210, 211, 212, 221],
            "moon": [800],
            "rain0": [300, 301, 302, 310, 311, 312, 313, 314, 321],
            "rain0_sun": [],
            "rain1": [502, 521, 522],
            "rain1_moon": [500, 501],
            "rain1_sun": [],
            "rain2": [503, 504, 531],
            "rain_lightning": [200, 201, 202, 230, 231, 232],
            "rain_snow": [511, 615, 616],
            "snow": [602, 613, 621, 622],
            "snow_moon": [600, 601, 611, 612, 620],
            "snow_sun": [],
            "sun": [],
            "wind": [771, 781],
        }

        def get_icon(code: int, daytime: bool = True):
            mapping = DAYTIME if daytime else NIGHTTIME

            for icon, codes in mapping.items():
                if code in codes:
                    return icon

        icon_code = data["weather"][0]["icon"]

        is_daytime = icon_code[-1] == "d"
        icon_name = get_icon(data["weather"][0]["id"], is_daytime)

        icon = Image.open(Path.cwd() / "icons" / "weather" / f"{icon_name}.png")

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

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))
        draw = ImageDraw.Draw(image)

        time_str = datetime.datetime.now().strftime("%H:%M")
        draw.text((39, 24), f"{time_str:>5}", font=font, fill=TIME_DATE_COLOR)

        if self.data is None:
            return image

        data = self.data

        temp: float = data["main"]["temp"]
        temp_f = int(k_to_f(temp))
        temp_c = int(k_to_c(temp))

        DAYTIME: dict[str, list[int]] = {
            "cloud": [803],
            "cloud_moon": [],
            "cloud_sun": [801, 802],
            "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
            "cloud_wind_moon": [],
            "cloud_wind_sun": [701],
            "clouds": [804],
            "lightning": [210, 211, 212, 221],
            "moon": [],
            "rain0": [302, 310, 311, 312, 313, 314, 321],
            "rain0_sun": [300, 301],
            "rain1": [502, 521, 522],
            "rain1_moon": [],
            "rain1_sun": [500, 501],
            "rain2": [503, 504, 531],
            "rain_lightning": [200, 201, 202, 230, 231, 232],
            "rain_snow": [511, 615, 616],
            "snow": [602, 613, 621, 622],
            "snow_moon": [],
            "snow_sun": [600, 601, 611, 612, 620],
            "sun": [800],
            "wind": [771, 781],
        }

        NIGHTTIME: dict[str, list[int]] = {
            "cloud": [803],
            "cloud_moon": [801, 802],
            "cloud_sun": [],
            "cloud_wind": [711, 721, 731, 741, 751, 761, 762],
            "cloud_wind_moon": [701],
            "cloud_wind_sun": [],
            "clouds": [804],
            "lightning": [210, 211, 212, 221],
            "moon": [800],
            "rain0": [300, 301, 302, 310, 311, 312, 313, 314, 321],
            "rain0_sun": [],
            "rain1": [502, 521, 522],
            "rain1_moon": [500, 501],
            "rain1_sun": [],
            "rain2": [503, 504, 531],
            "rain_lightning": [200, 201, 202, 230, 231, 232],
            "rain_snow": [511, 615, 616],
            "snow": [602, 613, 621, 622],
            "snow_moon": [600, 601, 611, 612, 620],
            "snow_sun": [],
            "sun": [],
            "wind": [771, 781],
        }

        def get_icon(code: int, daytime: bool = True):
            mapping = DAYTIME if daytime else NIGHTTIME

            for icon, codes in mapping.items():
                if code in codes:
                    return icon

        icon_code = data["weather"][0]["icon"]

        is_daytime = icon_code[-1] == "d"
        icon_name = get_icon(data["weather"][0]["id"], is_daytime)

        icon = Image.open(Path.cwd() / "icons" / "weather" / f"{icon_name}.png")

        image.paste(icon, (1, 0))
        draw.text((39, 0), f"{temp_f:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 5), "F", font=font, fill=TIME_DATE_COLOR)
        draw.text((39, 11), f"{temp_c:>2}°", font=bigfont, fill="#ffffff")
        draw.text((58, 16), "C", font=font, fill=TIME_DATE_COLOR)

        return image
