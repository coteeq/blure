from PIL import Image
from app import blure
from sanic.response import raw
from pathlib import Path
from io import BytesIO

_IMAGE_URL = blure.config.NGX_IMAGE_URL
_IMAGE_PATH = blure.config.NGX_IMAGE_PATH
_NOT_FOUND_IMAGE = blure.config.NOT_FOUND_IMAGE
_NOT_FOUND_IMAGE_CONTENT_TYPE = blure.config.NOT_FOUND_IMAGE_CONTENT_TYPE


class InvalidImageFormat(ValueError):
    pass


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

    @staticmethod
    def pillow_format(content_type: str):
        mapping = {
            '': 'PNG',  # try png if content type is not available
            'image/bmp': 'BMP',
            'image/gif': 'GIF',
            'image/jpeg': 'JPEG',
            'image/png': 'PNG'
        }
        if content_type in mapping.keys():
            return mapping[content_type]
        else:
            raise InvalidImageFormat(f'{content_type} is not supported')

    def save(self, body: BytesIO, content_type: str):
        image_path = Path(_IMAGE_PATH.format(self.filename))
        thumb_path = Path(_IMAGE_PATH.format(self.filename + '_thumb'))

        with image_path.open('wb') as f:
            f.write(body.getvalue())

        with thumb_path.open('wb') as f:
            im = Image.open(body)
            thumb_stream = BytesIO()
            im.thumbnail(blure.config.CUT_SIZES[2])
            im.save(thumb_stream, format=self.pillow_format(content_type))
            f.write(thumb_stream.getvalue())

    def delete_from_disk(self):
        image_path = Path(_IMAGE_PATH.format(self.filename))
        thumb_path = Path(_IMAGE_PATH.format(self.filename + '_thumb'))

        if image_path.exists():
            image_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()
