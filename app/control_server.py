import json
import uuid

import gevent
from app.application import Application
from app.user import User
from gevent.pool import Pool
from gevent.server import StreamServer


class ControlServer:
    def __init__(self):
        self.apps = {}
        self.pool = Pool(10000)

        app1 = Application('app1')
        self.apps[app1.id] = app1

    def gatekeeper(self, socket, address):
        sock_file = socket.makefile()

        data_login = json.loads(sock_file.readline())
        app_id = data_login['app_id']
        uid = data_login['uid']

        if app_id not in self.apps:
            socket.close()
            sock_file.close()
            return

        application = self.apps[app_id]

        prev_connected_user = application.get_user(uid)
        if prev_connected_user is not None:
            application.exit_user(prev_connected_user)

        new_user = User(uid=uid, guid=uuid.uuid4(), sock=socket, sock_file=sock_file, owner_app=application)
        application.enter_user(new_user)

        data_response_login = {
            'success': True,
            'guid': str(new_user.guid),
            'relay_server': {
                'ip': '127.0.0.1',
                'port': 10001
            }
        }
        new_user.sock.sendall('{}\n'.format(json.dumps(data_response_login)).encode('utf-8'))

        try:
            gevent.joinall(new_user.greenlets)
        finally:
            application.exit_user(new_user)

    def start_forever(self):
        StreamServer(('127.0.0.1', 10000), self.gatekeeper, spawn=self.pool).serve_forever()
