from PIL import Image
from app import blure
from sanic.response import raw, BaseHTTPResponse
from sanic.exceptions import NotFound
from pathlib import Path
from io import BytesIO

_IMAGE_URL = blure.config.NGX_IMAGE_URL
_IMAGE_PATH = blure.config.NGX_IMAGE_PATH
_NOT_FOUND_IMAGE = blure.config.NOT_FOUND_IMAGE
_NOT_FOUND_IMAGE_CONTENT_TYPE = blure.config.NOT_FOUND_IMAGE_CONTENT_TYPE


class InvalidImageFormat(ValueError):
    pass


async def is_image_exists(id: int):
    async with blure.pool.acquire() as conn:
        rec = await conn.fetchval('SELECT TRUE FROM pics WHERE id=$1', id)
        return rec is not None


class NGXImage:
    def __init__(self, from_id: int):
        self.id = from_id

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

    @classmethod
    async def create_from_bytes(cls, bytes_io: BytesIO, content_type: str):
        async with blure.pool.acquire() as conn:
            # TODO: make it a transaction
            new_id = await conn.fetchval(
                '''
                    INSERT INTO pics(src_url, content_type)
                    VALUES ($1, $2)
                    RETURNING id
                ''',
                '',
                content_type
            )

            ngx_image = NGXImage(from_id=new_id)

            with ngx_image.make_path('o').open('wb') as f:
                f.write(bytes_io.getvalue())

            image = Image.open(bytes_io)
            image.thumbnail(blure.config.CUT_SIZES['m'])
            image.save(
                ngx_image.make_path('m'),
                format=cls.pillow_format(content_type)
            )

            return ngx_image

    async def __aenter__(self):
        if not await is_image_exists(self.id):
            raise NotFound(
                f'image {blure.url.to_url(self.id)} does not exist'
            )
        else:
            return self

    async def __aexit__(self, *exc):
        pass

    def make_path(self, size: str='o') -> Path:
        return _IMAGE_PATH / Path(blure.url.to_url(self.id) + size)

    def make_url(self, size: str='o') -> Path:
        return _IMAGE_URL / Path(blure.url.to_url(self.id) + size)

    def send_image(self, size: str='o') -> BaseHTTPResponse:
        if not self.make_path(size).is_file():
            return self.not_found()

        return raw(b'',
                   content_type='image',
                   headers={'X-Accel-Redirect': self.make_url(size)},
                   status=200)

    @staticmethod
    def not_found():
        return raw(_NOT_FOUND_IMAGE,
                   content_type=_NOT_FOUND_IMAGE_CONTENT_TYPE,
                   status=404)

    async def delete_from_db(self):
        async with blure.pool.acquire() as conn:
            await conn.execute('DELETE FROM pics WHERE id=$1', self.id)

    def delete_from_disk(self):
        for cut_name in blure.config.CUT_SIZES.keys():
            path = self.make_path(cut_name)
            if path.exists():
                path.unlink()
