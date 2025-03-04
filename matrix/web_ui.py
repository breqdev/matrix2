import threading
import io
from PIL import Image
from flask import Flask, render_template, Response


class WebUI:
    def __init__(
        self, on_rotation_clockwise, on_rotation_counterclockwise, on_press
    ) -> None:
        self.frame_get = threading.Condition()
        self.frame: bytes | None = None

        self.app = Flask(__name__)

        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/preview")
        def preview():
            def generate_video_stream():
                yield b"--frame\r\nContent-Type: image/png\r\n\r\n"

                while True:
                    with self.frame_get:
                        self.frame_get.wait()

                    frame = self.frame
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

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self) -> None:
        self.app.run("0.0.0.0", 80)

    def send_frame(self, pil_frame: Image.Image) -> None:
        image_bytes = io.BytesIO()
        pil_frame.save(image_bytes, format="PNG")
        self.frame = image_bytes.getvalue()
        with self.frame_get:
            self.frame_get.notify_all()
