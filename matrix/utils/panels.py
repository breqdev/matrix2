from PIL import Image

from matrix.utils.config import PanelSize, get_panel_size


class Drawable:
    def get_image(self) -> Image.Image | None:
        """Get the current image for this screen. Delegates to size-specific methods by default.

        Screens can either:
        1. Override this method directly for size-agnostic rendering, or
        2. Override get_image_64x64() and get_image_64x32() for size-specific rendering
        """
        match get_panel_size():
            case PanelSize.PANEL_64x64:
                return self.get_image_64x64()
            case PanelSize.PANEL_64x32:
                return self.get_image_64x32()

    def get_image_64x64(self) -> Image.Image:
        """Get image for 64x64 panel. Override in subclasses for size-specific rendering."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_image_64x64() or override get_image()")

    def get_image_64x32(self) -> Image.Image:
        """Get image for 64x32 panel. Override in subclasses for size-specific rendering."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_image_64x32() or override get_image()")
