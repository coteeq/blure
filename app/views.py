from io import BytesIO
from .request_routine import db_route
from sanic.response import text, redirect, json
from jinja2_sanic import render_template
from app import blure
from requests import get as fetch_url
from .imutil import NGXImage
from .util import URLDecodeError
from sanic.exceptions import NotFound, InvalidUsage as BadRequest, ServerError


@blure.exception(NotFound)
async def not_found(req, exc):
    return render_template('404.html.j2', req, dict())


@blure.exception(URLDecodeError)
async def handle_urldecode(req, exc):
    raise ServerError(str(exc), status_code=400)


@db_route('/')
async def index(ctx):
    records = await ctx.pg.fetch('SELECT id FROM pics')
    picurls = [ctx.app.url.to_url(rec['id']) for rec in records]
    return render_template('index.html.j2', ctx.r, dict(picurls=picurls))


@db_route('/i/<url>')
async def raw_image(ctx, url):
    async with NGXImage(blure.url.to_id(url)) as image:
        return image.send_image('o')


@db_route('/t/<url>')
async def thumb_image(ctx, url):
    async with NGXImage(blure.url.to_id(url)) as image:
        return image.send_image('m')


@db_route('/p/<url>')
async def pic_profile(ctx, url):
    # Check image exists
    # This will be used to get meta
    async with NGXImage(blure.url.to_id(url)):
        return render_template('profile.html.j2',
                               ctx.r,
                               dict(url=url, tags=[]))


@db_route('/c/push', methods=['POST'])
async def pic_push(ctx):
    try:
        file = ctx.r.files['im'][0]
        image_stream = BytesIO(file.body)

        if len(ctx.r.form['content-type']) != 1:
            raise BadRequest('Need only one content-type')

        content_type = ctx.r.form['content-type'][0]

        image = await NGXImage.create_from_bytes(image_stream, content_type)

        return text(ctx.app.url.to_url(image.id))
    except KeyError:
        return text('you did not post anything')


@db_route('/c/push_url', methods=['POST'])
async def push_url(ctx):
    return redirect(ctx.app.url_for('index'))
    return json({'err': 'not_implemented'})
    response = fetch_url(ctx.r.json['url'])
    if response is None:
        return json({'err': 'fetch'})


@db_route('/c/delete/<url>', methods=['POST'])
async def delete_pic(ctx, url):
    id = ctx.app.url.to_id(url)
    async with NGXImage(id) as image:
        await image.delete_from_db()
        image.delete_from_disk()
    return redirect(ctx.app.url_for('index'))
