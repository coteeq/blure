from functools import wraps
from collections import namedtuple
from app import blure as app

Context = namedtuple('Context', [
    'r',   # request
    'pg',  # pg connection
    'app'  # r.app
])


def db_route(route, pool=True, **route_kwargs):
    def proxy_wrapper(f):
        @app.route(route, **route_kwargs)
        @wraps(f)
        async def wrapper(request, *args, **kwargs):
            if not pool:
                ctx = Context(r=request, pg=None, app=request.app)
                response = await f(ctx, *args, **kwargs)
            else:
                async with app.pool.acquire() as conn:
                    ctx = Context(r=request, pg=conn, app=request.app)
                    response = await f(ctx, *args, **kwargs)
            return response
        return wrapper
    return proxy_wrapper
