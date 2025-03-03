from abc import ABC, abstractmethod
from PIL import Image
import threading


class Screen(ABC):
    CACHE_TTL = 60

    def __init__(self):
        self.cached_data = None

        self.has_data = threading.Event()

        # use this thread to fetch the initial data immediately
        self.startup_thread = threading.Thread(target=self.handle_timer)
        self.startup_thread.start()

        # then, run with a timer
        self.timer = threading.Timer(self.CACHE_TTL, function=self.handle_timer)
        self.timer.start()

    def __del__(self):
        self.timer.cancel()

    def handle_timer(self):
        self.cached_data = self.fetch_data()
        self.has_data.set()

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
