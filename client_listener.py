import sys
import json
import time
import socket

BUF_SIZE = 1024

try:
    sock_channel_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_channel_control.connect(('127.0.0.1', 10000))
except ConnectionError as e:
    print('failed to connect control channel')
    sys.exit()

data_login = {
    'code': 1000,
    'app_id': 'app1',
    'uid': sys.argv[1]
}
sock_channel_control.send('{}\n'.format(json.dumps(data_login)).encode('utf-8'))
data = sock_channel_control.recv(BUF_SIZE).decode('utf-8')
print(data)

data_response_login = json.loads(data)

address_data_channel = (data_response_login['relay_server']['ip'], data_response_login['relay_server']['port'])

sock_channel_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_channel_data.connect(address_data_channel)

data = '{} '.format(data_response_login['guid'])
sock_channel_data.send(data.encode('utf-8'))


while True:
    time.sleep(1)

    data, addr = sock_channel_data.recvfrom(BUF_SIZE)
    data = data.decode('utf-8').rstrip()
    print('[data] {}'.format(data))
