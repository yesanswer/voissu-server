from gevent.server import DatagramServer


class RelayServer(DatagramServer):
    def __init__(self, control_server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.control_server = control_server

    def handle(self, data, address):
        if len(data) < 36:
            # skip invalid datagram
            return

        print('{}: got {}'.format(address, data.decode('utf-8')))

        guid = data[:36].decode('utf-8')
        if guid not in self.control_server.users:
            return

        broadcast_data = data[37:]

        sender = self.control_server.users[guid]
        if not hasattr(sender, 'data_channel_address'):
            sender.data_channel_address = address

        app = sender.owner_app
        users = app.users.values()
        for user in users:
            if hasattr(user, 'data_channel_address'):
                self.socket.sendto(broadcast_data, user.data_channel_address)
