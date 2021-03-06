import struct

from gevent.server import DatagramServer


class UdpMessage:
    def __init__(self, data):
        self.guid = data[:36].decode('utf-8')
        self.kind = struct.unpack('i', data[36:40])[0]

        if self.kind == 0:
            self.seq = 0
            self.broadcast_data = b''
        else:
            self.seq = struct.unpack('i', data[40:44])[0]
            self.broadcast_data = data[44:]

    def __repr__(self):
        return '{} {} {} {}'.format(self.guid, self.kind, self.seq, self.broadcast_data)

    def to_bytes(self, sender_uid):
        data = b''.join([
            ('%-36s' % sender_uid).encode('utf8'),
            struct.pack('i', self.kind),
            struct.pack('i', self.seq),
            self.broadcast_data
        ])
        return data


class RelayServer(DatagramServer):
    def __init__(self, control_server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.control_server = control_server

    def handle(self, data, address):
        if len(data) < 40:
            # skip invalid datagram
            return

        msg = UdpMessage(data)

        sender = self.control_server.get_user_by_guid(msg.guid)
        if sender is None:
            return

        print('{} send : {}'.format(sender.uid, msg))

        if sender.public_address is None:
            sender.public_address = address

        if msg.kind == 0:
            # skip broadcasting if this message is login message
            return

        if sender.owner_channel:
            sender.owner_channel.broadcast_by_relay_server(self, sender, msg)
