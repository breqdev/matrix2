from typing import Optional
from PIL import Image
import requests
import io

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from matrix.cache import ttl_cache

scope = "user-read-currently-playing user-read-playback-state"

# Listed in order of precedence
SPOTIFY_ACCOUNTS = [
    "Brooke",
    "Ava",
]

spotify_clients: dict[str, spotipy.Spotify] = {}


for account in SPOTIFY_ACCOUNTS:
    print(f"Logging in {account}...")
    auth_manager = SpotifyOAuth(
        scope=scope, open_browser=False, cache_path=f".spotipy-cache-${account}"
    )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    spotify_clients[account] = sp


@ttl_cache(seconds=15)
def get_image_spotify() -> Optional[Image.Image]:
    image = Image.new("RGB", (64, 64))

    for sp in spotify_clients.values():
        state = sp.current_user_playing_track()
        if state and state["item"]:
            break
    else:
        return None

    cover_url = state["item"]["album"]["images"][0]["url"]
    image_data = requests.get(cover_url).content

    image.paste(Image.open(io.BytesIO(image_data)).resize((64, 64)))

    return image
