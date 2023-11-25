from aiohttp import web
app = web.Application()

from views import *

app.router.add_get('/', root)
app.router.add_get('/chat_ws', chat_ws)
app.router.add_get('/user_exists', user_exists)
app.router.add_get('/shutdown', shutdown_server)

app.router.add_get('/profile/username', my_username)
app.router.add_get('/profile/edit/username', change_username)
app.router.add_post('/profile/edit/password', change_password)

app.router.add_post('/login/signup', sign_up)
app.router.add_post('/chat', chat)

app.router.add_get('/{p:.*}', file)


app.on_shutdown.append(lambda: print('App shutdown.'))
web.run_app(app, port=33898)
