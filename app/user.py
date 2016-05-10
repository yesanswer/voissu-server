from gevent.queue import Queue


class User:
    def __init__(self, uid, guid, sock, sock_file, owner_app):
        self.uid = uid
        self.guid = guid
        self.sock = sock
        self.sock_file = sock_file
        self.gevent_queue = Queue()
        self.owner_app = owner_app

    def reader(self):
        for line in self.sock_file:
            self.owner_app.broadcast(line)

    def writer(self):
        while True:
            msg = self.gevent_queue.get()
            print(msg)

            if isinstance(msg, str):
                encoded = msg.encode('utf-8')
                self.sock.sendall(encoded)
            elif isinstance(msg, bytes):
                self.sock.sendall(msg)

    def disconnect(self):
        pass
