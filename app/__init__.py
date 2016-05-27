from app.control_server import ControlServer
from app.relay_server import RelayServer

control_server = ControlServer()
relay_server = RelayServer(control_server, '*:10001')
