import json
import uuid

import gevent
from app.app import App
from app.channel import Channel
from app.user import User
from gevent.pool import Pool
from gevent.server import StreamServer

apps = {}

app1 = App('app1')
apps[app1.id] = app1


def gatekeeper(socket, address):
    sock_file = socket.makefile()

    data_login = json.loads(sock_file.readline())
    app_id = data_login['app_id']
    uid = data_login['uid']

    if app_id not in apps:
        return

    application = apps[app_id]

    prev_connected_user = application.get_user(uid)
    if prev_connected_user is not None:
        application.exit_user(prev_connected_user)

    new_user = User(uid=uid, guid=uuid.uuid4(), sock=socket, sock_file=sock_file, owner_app=application)
    application.enter_user(new_user)

    new_user.sock.sendall('{}\n'.format(json.dumps({'success': True, 'guid': str(new_user.guid)})).encode('utf-8'))

    try:
        gevent.joinall(new_user.greenlets)
    finally:
        application.exit_user(new_user)


pool = Pool(10000)
app = StreamServer(('127.0.0.1', 10000), gatekeeper, spawn=pool)
