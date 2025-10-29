from collections.abc import Callable
import logging
import threading
import io
from PIL import Image
from flask import Flask, render_template, Response, request
from werkzeug import serving

logger = logging.getLogger(__name__)

serving._log_add_style = False


class WebUI:
    def __init__(
        self,
        *,
        port: int,
        on_rotation_clockwise: Callable[[], None],
        on_rotation_counterclockwise: Callable[[], None],
        on_press: Callable[[], None],
    ) -> None:
        self.frame_get = threading.Condition()
        self.frame: bytes | None = None

        self.app = Flask(__name__)

        @self.app.route("/")
        def index():
            logger.info(
                "New connection from %s via '%s'",
                request.remote_addr,
                request.user_agent,
            )
            return render_template("index.html")

        @self.app.route("/preview")
        def preview():
            def generate_video_stream():
                yield b"--frame\r\nContent-Type: image/png\r\n\r\n"

                while True:
                    with self.frame_get:
                        self.frame_get.wait()

                    frame = self.frame
                    assert frame
                    yield frame + b"\r\n--frame\r\nContent-Type: image/png\r\n\r\n"

            return Response(
                generate_video_stream(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

        @self.app.route("/actions/clockwise", methods=["POST"])
        def clockwise():
            on_rotation_clockwise()
            return "", 204

        @self.app.route("/actions/counterclockwise", methods=["POST"])
        def counterclockwise():
            on_rotation_counterclockwise()
            return "", 204

        @self.app.route("/actions/press", methods=["POST"])
        def press():
            on_press()
            return "", 204

        self.thread = threading.Thread(target=self.run, args=(port,))
        self.thread.start()

    def run(self, port: int) -> None:
        self.app.run("0.0.0.0", port)

    def send_frame(self, pil_frame: Image.Image) -> None:
        image_bytes = io.BytesIO()
        pil_image = Image.new("RGB", (64, 64), (255, 0, 255))
        pil_image.paste(pil_frame)
        pil_image.save(image_bytes, format="PNG")
        self.frame = image_bytes.getvalue()
        with self.frame_get:
            self.frame_get.notify_all()
