import os
import requests
import datetime

from PIL import Image, ImageDraw

from matrix.fonts import font, bigfont

weather_api_key = os.environ["OPENWEATHERMAP_KEY"]
weather_base_url = "https://api.openweathermap.org/data/2.5/weather?"
zip_code = os.getenv("ZIP_CODE", "02145")

weather_url = weather_base_url + "appid=" + weather_api_key + "&zip=" + zip_code

def k_to_f(k: float) -> float:
    return (k - 273.15) * 9 / 5 + 32


def k_to_c(k: float) -> float:
    return k - 273.15

def get_image_weather() -> Image.Image:
    image = Image.new("RGB", (64, 64))
    draw = ImageDraw.Draw(image)

    date_str = datetime.datetime.now().strftime("%m/%d")
    time_str = datetime.datetime.now().strftime("%H:%M")
    draw.text((0, 1), f"{date_str:<5}   {time_str:>5}", font=font, fill="#ffffff")

    data = requests.get(weather_url).json()

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

    icon = Image.open(os.path.join("weather-pixel-icons", "32", f"{icon_name}.xbm"))

    image.paste(icon, (1, 11))
    draw.text((36, 13), f"{temp_f:>2}°", font=bigfont, fill="#ffffff")
    draw.text((57, 13), "F", font=bigfont, fill="#ffffff")
    draw.text((36, 27), f"{temp_c:>2}°", font=bigfont, fill="#ffffff")
    draw.text((57, 27), "C", font=bigfont, fill="#ffffff")

    draw.line((4, 51, 6, 49, 8, 51), fill="#ffffff")
    draw.text((14, 47), f"{temp_max_f:>2}°F  {temp_max_c:>2}°C", font=font, fill="#ffffff")
    draw.line((4, 57, 6, 59, 8, 57), fill="#ffffff")
    draw.text((14, 55), f"{temp_min_f:>2}°F  {temp_min_c:>2}°C", font=font, fill="#ffffff")

    return image
