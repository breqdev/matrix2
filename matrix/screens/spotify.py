from PIL import Image
import requests
import io

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from matrix.screens.screen import Screen

scope = "user-read-currently-playing user-read-playback-state"

# Listed in order of precedence
SPOTIFY_ACCOUNTS = [
    "Brooke",
    "Ava",
]


class Spotify(Screen[Image.Image | None]):
    CACHE_TTL = 15
    has_login = False
    spotify_clients: dict[str, spotipy.Spotify] = {}

    def fetch_data(self):
        if not self.has_login:
            for account in SPOTIFY_ACCOUNTS:
                print(f"Logging in {account}...")
                auth_manager = SpotifyOAuth(
                    scope=scope,
                    open_browser=False,
                    cache_path=f".spotipy-cache-${account}",
                )
                sp = spotipy.Spotify(auth_manager=auth_manager)
                self.spotify_clients[account] = sp

            self.has_login = True

        for sp in self.spotify_clients.values():
            state = sp.current_user_playing_track()
            if state and state["item"]:
                cover_url = state["item"]["album"]["images"][0]["url"]
                image_data = requests.get(cover_url).content
                return Image.open(io.BytesIO(image_data)).resize((64, 64))

        return None

    def get_image(self):
        if data := self.data:
            image = Image.new("RGB", (64, 64))
            image.paste(data)
            return image
        return None

    @property
    def is_active(self):
        return self.data is not None
