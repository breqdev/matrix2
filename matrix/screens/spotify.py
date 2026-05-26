import io

import requests
import spotipy
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth

from matrix.screens.screen import Screen

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
                image_data = self.fetch_url(cover_url).content
                return Image.open(io.BytesIO(image_data)).resize((64, 64))

        return None

    def fallback_data(self):
        return None

    def get_image_64x64(self):
        image = Image.new("RGB", (64, 64))

        if data := self.data:
            image.paste(data)

        return image

    def get_image_64x32(self):
        image = Image.new("RGB", (64, 32))

        if data := self.data:
            image.paste(data.resize((32, 32)), (16, 0))

        return image

    @property
    def is_active(self):
        return self.is_enabled and self.data is not None
