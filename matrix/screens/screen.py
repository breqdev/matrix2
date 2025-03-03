from abc import ABC, abstractmethod
from PIL import Image
import threading


class Screen(ABC):
    CACHE_TTL = 60

    def __init__(self):
        self.cached_data = None

        self.has_data = threading.Event()
        self.cancel_timer = threading.Event()

        self.thread = threading.Thread(target=self.background_fetcher)
        self.thread.start()

    def __del__(self):
        self.cancel_timer.set()

    def background_fetcher(self):
        while True:
            try:
                self.cached_data = self.fetch_data()
                self.has_data.set()
            except Exception as e:
                print(e)

            if self.cancel_timer.wait(timeout=self.CACHE_TTL):
                return

    def fetch_data(self):
        """Fetch the latest data for this screen."""
        pass

    @property
    def data(self):
        """Return the latest cached data."""
        self.has_data.wait()
        return self.cached_data

    @abstractmethod
    def get_image(self) -> Image.Image | None:
        """Render an image."""
        pass
