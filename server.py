from app import control_server, relay_server

if __name__ == '__main__':
    relay_server.start()
    control_server.start_forever()
