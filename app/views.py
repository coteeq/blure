from io import BytesIO
from .request_routine import db_route
from sanic.response import text, redirect, json
from jinja2_sanic import render_template
from app import log
from requests import get as fetch_url
from .imutil import NGXImage


@db_route('/')
async def index(ctx):
    records = await ctx.pg.fetch('SELECT id FROM pics')
    picurls = [ctx.app.url.to_url(rec['id']) for rec in records]
    return render_template('index.html.j2', ctx.r, dict(picurls=picurls))


@db_route('/i/<url>')
async def raw_image(ctx, url):
    id = ctx.app.url.to_id(url)
    if id is None:
        return NGXImage.not_found()

    name = await ctx.pg.fetchval('SELECT 1 FROM pics WHERE id=$1', id)
    if name is None:
        log.error('Image not in db')
        return NGXImage.not_found()

    return NGXImage(id).orig()


@db_route('/t/<url>')
async def thumb_image(ctx, url):
    id = ctx.app.url.to_id(url)
    if id is None:
        return NGXImage.not_found()

    name = await ctx.pg.fetchval('SELECT 1 FROM pics WHERE id=$1', id)
    if name is None:
        log.error('Image not in db')
        return NGXImage.not_found()

    return NGXImage(id).thumb()


@db_route('/p/<url>')
async def pic_profile(ctx, url):
    return render_template('profile.html.j2', ctx.r, dict(url=url, tags=[]))


@db_route('/c/push', methods=['POST'])
async def pic_push(ctx):
    try:
        file = ctx.r.files['im'][0]
        image_stream = BytesIO(file.body)
        ext = file.name.split('.')[-1]
        id = await ctx.pg.fetchval(
            'INSERT INTO pics(src_url, ext) VALUES ($1, $2) RETURNING id', '', ext
        )

        im = NGXImage(id)
        im.save(image_stream)

        return text('new url is ' + ctx.app.url.to_url(id))
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
    await ctx.pg.execute('DELETE FROM pics WHERE id=$1', id)
    im = NGXImage(id)
    im.delete_from_disk()
    return redirect(ctx.app.url_for('index'))