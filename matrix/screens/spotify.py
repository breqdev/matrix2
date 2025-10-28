from PIL import Image
import requests
import io

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from matrix.screens.screen import REQUEST_DEFAULT_TIMEOUT, Screen

scope = "user-read-currently-playing user-read-playback-state"


class Spotify(Screen[Image.Image | None]):
    CACHE_TTL = 15
    has_login = False
    spotify_clients: dict[str, spotipy.Spotify] = {}

    def fetch_data(self):
        if not self.has_login:
            for account in self.config["users"]:
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
                image_data = requests.get(cover_url, timeout=REQUEST_DEFAULT_TIMEOUT).content
                return Image.open(io.BytesIO(image_data)).resize((64, 64))

        return None

    def fallback_data(self):
        return None

    def get_image_64x64(self):
        if data := self.data:
            image = Image.new("RGB", (64, 64))
            image.paste(data)
            return image
        return None

    def get_image_64x32(self):
        if data := self.data:
            image = Image.new("RGB", (64, 32))
            image.paste(data.resize((32, 32)), (16, 0))
            return image
        return None

    @property
    def is_active(self):
        return self.is_enabled and self.data is not None
