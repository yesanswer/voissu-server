from gevent.server import DatagramServer


class RelayServer(DatagramServer):
    def __init__(self, control_server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.control_server = control_server

    def handle(self, data, address):
        print('{}: got {}'.format(address[0], data))
