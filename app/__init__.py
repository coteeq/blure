from sanic import Sanic
import config
from asyncpg import create_pool
import jinja2_sanic
from jinja2 import FileSystemLoader
import logging
from .in_log import LOG_SETTINGS
from .util import URLCoder
from .schema import schema_up

blure = Sanic(__name__, log_config=LOG_SETTINGS)
log = logging.getLogger('blure')

jinja2_sanic.setup(blure, loader=FileSystemLoader('app/templates'))
blure.config.from_object(config)
blure.static('/static', './app/static')
blure.url = URLCoder(blure.config.APP_SECRET[::2])  # cut secret, because it is too long


@blure.listener('before_server_start')
async def setup_db(_app, loop):
    _app.pool = await create_pool(_app.config.PG_URI, loop=loop)
    async with _app.pool.acquire() as conn:
        await create_tables(conn)


@blure.listener('after_server_stop')
async def close_db_conns(_app, loop):
    await _app.pool.close()


from . import views  # noqa # unused-import, E402


async def create_tables(conn):
    async with conn.transaction():
        for statement in schema_up:
            await conn.execute(statement)
