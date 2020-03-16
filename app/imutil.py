from PIL import Image
from app import blure
from sanic.response import raw
from pathlib import Path
from io import BytesIO

_IMAGE_URL = blure.config.NGX_IMAGE_URL
_IMAGE_PATH = blure.config.NGX_IMAGE_PATH
_NOT_FOUND_IMAGE = blure.config.NOT_FOUND_IMAGE
_NOT_FOUND_IMAGE_CONTENT_TYPE = blure.config.NOT_FOUND_IMAGE_CONTENT_TYPE


class NGXImage:
    def __init__(self, id: int):
        self.filename = blure.url.to_url(id)

    @staticmethod
    def _load_pic(filename):
        p = Path(_IMAGE_PATH.format(filename))
        if not p.is_file():
            return NGXImage.not_found()

        return raw(b'',
                   content_type='image',
                   headers={'X-Accel-Redirect': _IMAGE_URL.format(filename)},
                   status=200)

    def orig(self):
        return self._load_pic(self.filename)

    def thumb(self):
        return self._load_pic(self.filename + '_thumb')

    @staticmethod
    def not_found():
        return raw(_NOT_FOUND_IMAGE,
                   content_type=_NOT_FOUND_IMAGE_CONTENT_TYPE,
                   status=404)

    def save(self, body: BytesIO):
        image_path = Path(_IMAGE_PATH.format(self.filename))
        thumb_path = Path(_IMAGE_PATH.format(self.filename + '_thumb'))

        with image_path.open('wb') as f:
            f.write(body.getvalue())

        with thumb_path.open('wb') as f:
            im = Image.open(body)
            thumb_stream = BytesIO()
            im.thumbnail(blure.config.CUT_SIZES[2])
            im.save(thumb_stream, format='JPEG')
            f.write(thumb_stream.getvalue())

    def delete_from_disk(self):
        image_path = Path(_IMAGE_PATH.format(self.filename))
        thumb_path = Path(_IMAGE_PATH.format(self.filename + '_thumb'))

        if image_path.exists():
            image_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()
