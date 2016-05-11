import gevent
from gevent.queue import Queue


class User:
    def __init__(self, uid, guid, sock, sock_file, owner_app):
        self.uid = uid
        self.guid = guid
        self.sock = sock
        self.sock_file = sock_file
        self.gevent_queue = Queue()
        self.owner_app = owner_app
        self.closed = False
        self.greenlets = [gevent.spawn(self.reader),
                          gevent.spawn(self.writer)]

    def reader(self):
        for line in self.sock_file:
            self.owner_app.broadcast(line)

    def writer(self):
        while True:
            msg = self.gevent_queue.get()
            print('[{}] {} : {}'.format(self.owner_app.id, self.uid, msg.rstrip()))

            if isinstance(msg, str):
                encoded = msg.encode('utf-8')
                self.sock.sendall(encoded)
            elif isinstance(msg, bytes):
                self.sock.sendall(msg)

    def disconnect(self):
        if not self.closed:
            self.sock.close()
            self.closed = True
            gevent.killall(self.greenlets)
