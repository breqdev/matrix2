from typing import Optional
from PIL import Image
import requests
import os
import io

import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-read-currently-playing user-read-playback-state"

cache_dir = '.cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

os.chmod(cache_dir, 0o777)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))


def get_image_spotify() -> Optional[Image.Image]:
    image = Image.new("RGB", (64, 64))

    state = sp.current_user_playing_track()
    if state is None:
        return None

    cover_url = state["item"]["album"]["images"][0]["url"]
    image_data = requests.get(cover_url).content

    image.paste(Image.open(io.BytesIO(image_data)).resize((64, 64)))

    return image
