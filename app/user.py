import json

import gevent
from app.message_types import *
from gevent.queue import Queue


class User:
    def __init__(self, uid, guid, sock, sock_file, owner_app):
        self.uid = uid
        self.guid = guid
        self.sock = sock
        self.sock_file = sock_file
        self.gevent_queue = Queue()
        self.owner_app = owner_app
        self.owner_channel = None

        # 아래의 두 주소는 각각 공인, 사설 udp 주소
        self.public_address = None
        self.private_address = None
        self.closed = False
        self.greenlets = [gevent.spawn(self.reader),
                          gevent.spawn(self.writer)]

    def reader(self):
        for line in self.sock_file:
            req = json.loads(line)
            self.handle_request(req)

    def writer(self):
        while True:
            msg = self.gevent_queue.get()
            print('[{}] {} : {}'.format(self.owner_app.id, self.uid, msg.rstrip()))

            if isinstance(msg, str):
                encoded = msg.encode('utf-8')
                self.sock.sendall(encoded)
            elif isinstance(msg, bytes):
                self.sock.sendall(msg)
            elif isinstance(msg, dict):
                data = json.dumps(msg)
                encoded = data.encode('utf-8')
                self.sock.sendall(encoded)

    def disconnect(self):
        if not self.closed:
            gevent.killall(self.greenlets)
            self.sock.close()
            self.sock_file.close()
            self.closed = True

    def handle_request(self, req):
        request_type = req['type']
        if request_type == 1000:
            pass
        elif request_type == REQUEST_TYPE_SIGN_OUT:
            self.handle_request_sign_out(req)
            pass
        elif request_type == REQUEST_TYPE_PING:
            pass
        elif request_type == REQUEST_TYPE_ENTER_CHANNEL:
            self.handle_request_enter_channel(req)
        elif request_type == REQUEST_TYPE_EXIT_CHANNEL:
            self.handle_request_exit_channel(req)
        elif request_type == REQUEST_TYPE_P2P_CONNECT_SUCCESS:
            pass
        elif request_type == REQUEST_TYPE_P2P_CONNECT_FAIL:
            pass
        elif request_type == REQUEST_TYPE_MIC_ON:
            pass
        elif request_type == REQUEST_TYPE_MIC_OFF:
            pass
        elif request_type == REQUEST_TYPE_CHECK_EXIST_CHANNEL:
            self.handle_request_check_exist_channel(req)

    def handle_request_sign_out(self, req):
        raise NotImplemented

    def handle_request_enter_channel(self, req):
        while self.public_address is not None:
            gevent.sleep(0)

        channel_id = req['channel_id']
        self.owner_app.enter_channel(self)
        if channel_id not in self.owner_app.channels:
            # channel not found
            pass

        self.private_address = req['private_udp_address']

        self.owner_app.enter_channel(channel_id, self)

    def handle_request_exit_channel(self, req):
        channel_id = req['channel_id']
        if channel_id not in self.owner_app.channels:
            # channel not found
            pass

        self.owner_app.exit_channel(channel_id, self)

    def handle_request_check_exist_channel(self, req):
        channel_id = req['channel_id']

        is_exist = self.owner_app.check_exist_channel(channel_id)
        self.gevent_queue.put({
            'type': RESPONSE_TYPE_CHECK_EXIST_CHANNEL,
            'exist': is_exist
        })
