from PIL import Image

import qrcode


from matrix.screens.screen import Screen


class QRCode(Screen):
    def get_image(self):
        image = Image.new("RGB", (64, 64))

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data("https://avasilver.dev/")
        qr.make(fit=True)

        img = qr.make_image(fill_color="#cccccc", back_color="#000000")
        padding = (64 - (img.width + img.border * 2) * img.box_size) // 2
        image.paste(img, (padding, padding))

        return image
