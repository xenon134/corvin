from aiohttp import web, WSMsgType
from backend import *

import pathlib
website_root = pathlib.Path('website').absolute()
async def file(request):
    f = (website_root / request.match_info['p']).absolute()
    if website_root not in f.parents:
        print('Refused:', f)
        raise web.HTTPNotFound()
    if f.is_dir():
        f = f / 'index.html'
    if f.is_file():
        print('Served:', f, 'to', request.path)
        return web.FileResponse(f)
    else: # doesnt exist
        print('404:', f)
        raise web.HTTPNotFound()

async def root(request):
    
    raise web.HTTPMovedPermanently(location='/login')

async def sign_up(request):
    data = await request.post()
    if not User.create(data['usn'], data['pwd']): # user already exists
        raise web.HTTPFound(location='/login/sign_up.html?ic=u')
    raise web.HTTPFound(location='/login')


async def chat(request):
    if request.method == 'GET':
        return file(request)
    # else POST
    data = await request.post()
    print('Recieved login request:', data['usn'], data['pwd'])

    user = User.for_username(data['usn'])
    if not user: # user not found
        raise web.HTTPFound(location='/login?ic=u')
    if not user.check_password(data['pwd']):
        raise web.HTTPFound(location='/login?ic=p')

    res = web.FileResponse('website\\chat\\index.html')
    res.set_cookie('authtoken', user.login())
    return res

activeConnections = set()
async def chat_ws(request):
    print('Recieved Websocket request.')
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    try:
        authtoken = request.cookies['authtoken']
    except KeyError:
        await ws.send_str('n') # bad authtoken
        await ws.close()
        return
    user = User.for_authtoken(authtoken)
    if not user:
        await ws.send_str('b') # bad authtoken
        await ws.close()
        return

    chats___ = user.allChats()
    await ws.send_str(chats___)
    print('Sent:', chats___)

    activeConnections.add((user, ws))
    import json
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            msgStr = data['msgStr']
            to = User.for_username(data['with'])
            user.sendMsg(to, msgStr)
            for iUser, iWs in activeConnections:
                if iUser == to:
                    await iWs.send_json([{
                        'with': user.username,
                        'messages': [{'sent': False, 'data': msgStr}]
                    }])
                    break # a user cannot be logged in two places at once
            await ws.send_json([{
                'with': to.username,
                'messages': [{'sent': True, 'data': msgStr}]
            }])

    activeConnections.remove((user, ws))
    return ws

async def user_exists(request):
    us = User.for_username(request.query['u'])
    return web.Response(text=('1' if us else ''))


# Profile related:
def authenticate(request):
    try:
        user = User.for_authtoken(request.cookies['authtoken'])
    except KeyError: # authtoken cookie not present
        raise web.HTTPUnauthorized()
    if user:
        return user
    else:
        raise web.HTTPUnauthorized()

async def my_username(request):
    user = authenticate(request)
    return web.Response(text=user.username)

async def change_username(request):
    user = authenticate(request)
    newUsn = request.query['u']
    if User.for_username(newUsn): # username already in use
        return web.Response(text='')
    user.username = request.query['u']
    return web.Response(text='1')

async def change_password(request):
    user = authenticate(request)
    user.changePassword(await request.text())
    return web.Response(text='')

async def shutdown_server(request):
    if User.for_authtoken(request.cookies['authtoken']).username == 'admin':
        print('Shutdown request authorized.')
        raise web.GracefulExit()
    else:
        print('Shutdown request not authorized.')
        raise web.HTTPForbidden()
