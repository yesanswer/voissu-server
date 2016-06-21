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

    def to_bytes(self, sender_uid):
        data = b''.join([
            ('%-36s' % sender_uid).encode('utf8'),
            struct.pack('i', 0),
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

        print('{}: got {}'.format(address, data))

        msg = UdpMessage(data)

        sender = self.control_server.get_user_by_guid(msg.guid)
        if sender is None:
            return

        if sender.public_address is None:
            sender.public_address = address

        if msg.kind == 0:
            # skip broadcasting if this message is login message
            return

        broadcast_data = msg.to_bytes(sender.uid)

        if sender.channel:
            sender.channel.broadcast_by_relay_server(self, broadcast_data)
