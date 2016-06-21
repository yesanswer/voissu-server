import json
import uuid

import gevent
from app.application import Application
from app.message_types import *
from app.user import User
from gevent.pool import Pool
from gevent.server import StreamServer


class ControlServer:
    def __init__(self):
        self.apps = {}
        self.pool = Pool(10000)
        self.users = {}

        app1 = Application('app1')
        self.apps[app1.id] = app1

    def gatekeeper(self, socket, address):
        print('{} connected'.format(address))
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
            del(self.users[prev_connected_user.guid])

        new_user_guid = str(uuid.uuid4())

        data_response_login = {
            'success': True,
            'type': RESPONSE_TYPE_SIGN_IN,
            'guid': new_user_guid,
            'relay_server': {
                'ip': '127.0.0.1',
                'port': 10001
            }
        }
        socket.sendall('{}\n'.format(json.dumps(data_response_login)).encode('utf-8'))

        new_user = User(uid=uid, guid=new_user_guid, sock=socket, sock_file=sock_file, owner_app=application)
        application.enter_user(new_user)
        self.users[new_user.guid] = new_user

        try:
            gevent.joinall(new_user.greenlets)
        finally:
            application.exit_user(new_user)

    def start_forever(self):
        StreamServer(('0.0.0.0', 10000), self.gatekeeper, spawn=self.pool).serve_forever()

    def get_user_by_guid(self, guid):
        return self.users[guid] if guid in self.users else None
