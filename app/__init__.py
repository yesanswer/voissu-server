import uuid

import gevent
from gevent.pool import Pool
from gevent.queue import Queue
from gevent.server import StreamServer

users = {}


def broadcast(msg):
    msg = '{}\n'.format(msg)
    for v in users.values():
        v.put(msg)


def reader(username, f):
    for l in f:
        msg = '{}> {}'.format(username, l.strip())
        print("[system] read from socket({}) : {}", f, msg)
        broadcast(msg)


def writer(q, sock):
    while True:
        msg = q.get()
        if isinstance(msg, str):
            encoded = msg.encode('utf-8')
            sock.sendall(encoded)
        elif isinstance(msg, bytes):
            sock.sendall(msg)


def gatekeeper(socket, address):
    f = socket.makefile()

    name = uuid.uuid4()

    print("[system] new user {} - socket({})".format(name, socket))

    socket.sendall('your name is {}'.format(name).encode('utf-8'))
    broadcast('[system] %s joined from %s.' % (name, address[0]))

    try:
        q = Queue()
        users[name] = q

        r = gevent.spawn(reader, name, f)
        w = gevent.spawn(writer, q, socket)
        gevent.joinall([r, w])
    finally:
        del (users[name])
        broadcast('[system] %s left the chat.' % name)


pool = Pool(10000)
app = StreamServer(('127.0.0.1', 10000), gatekeeper, spawn=pool)
