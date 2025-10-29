import logging
import threading
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from datadog.dogstatsd.base import statsd

from matrix.utils.panels import Drawable, PanelSize

logger = logging.getLogger(__name__)

REQUEST_DEFAULT_TIMEOUT = 15
CACHE_TTL = 60

T = TypeVar("T")


class Screen(ABC, Drawable, Generic[T]):
    def __init__(self, config: dict, size: PanelSize) -> None:
        self.config = config
        self.size = size
        self.cached_data: T

        self.has_data = threading.Event()
        self.cancel_timer = threading.Event()

        self.thread = threading.Thread(target=self.background_fetcher)
        self.thread.start()

        self.is_enabled = True

    def cancel(self) -> None:
        self.cancel_timer.set()

    def __del__(self) -> None:
        self.cancel()

    @property
    def is_active(self) -> bool:
        """Return if the screen should be displayed"""
        return self.is_enabled

    def background_fetcher(self) -> None:
        while True:
            try:
                t0 = time.time()
                self.cached_data = self.fetch_data()
                statsd.gauge(
                    "matrix.load_seconds",
                    time.time() - t0,
                    tags=[f"image:{self.__class__.__name__}"],
                )
            except Exception as e:
                logger.exception("Error while fetching data: %s", e)
                self.cached_data = self.fallback_data()
            finally:
                self.has_data.set()

            if self.cancel_timer.wait(timeout=CACHE_TTL):
                return

    @abstractmethod
    def fetch_data(self) -> T:
        """Fetch the latest data for this screen."""

    @abstractmethod
    def fallback_data(self) -> T:
        """Return fallback data if requesting data fails."""
        pass

    @property
    def data(self) -> T:
        """Return the latest cached data."""
        self.has_data.wait()
        return self.cached_data

    def get_time_stretch(self) -> float | None:
        """Screens can return a duration here to increase the amount of time displayed.

        Useful for temporary conditions that require more time, such as
        scrolling alert messages.
        """
        return None
