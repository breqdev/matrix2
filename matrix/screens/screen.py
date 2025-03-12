from abc import ABC, abstractmethod
from PIL import Image
import threading
import time
import logging

from datadog.dogstatsd.base import statsd


logger = logging.getLogger(__name__)


class Screen(ABC):
    CACHE_TTL = 60

    def __init__(self):
        self.cached_data = None

        self.has_data = threading.Event()
        self.cancel_timer = threading.Event()

        self.thread = threading.Thread(target=self.background_fetcher)
        self.thread.start()

    def cancel(self):
        self.cancel_timer.set()

    def __del__(self):
        self.cancel()

    @property
    def is_active(self):
        return True

    def background_fetcher(self):
        while True:
            try:
                t0 = time.time()
                self.cached_data = self.fetch_data()
                statsd.gauge(
                    "matrix.load_seconds",
                    time.time() - t0,
                    tags=[f"image:{self.__class__.__name__}"],
                )
                self.has_data.set()
            except Exception as e:
                logger.exception("Error while fetching data: %s", e)

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
