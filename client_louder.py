import json
import socket
import struct
import sys
import time

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
    'uid': 'user1'
}
sock_channel_control.send('{}\n'.format(json.dumps(data_login)).encode('utf-8'))
data = sock_channel_control.recv(BUF_SIZE).decode('utf-8')
print(data)

data_response_login = json.loads(data)

keyword = sys.argv[1]
count = 0
guid = data_response_login['guid']

address_data_channel = (data_response_login['relay_server']['ip'], data_response_login['relay_server']['port'])

sock_channel_data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    word = '{}{}'.format(keyword, count)
    data = b''.join([
        guid.encode('utf8'),
        struct.pack('i', 0),
        struct.pack('i', 0),
        word.encode('utf8')
    ])
    sock_channel_data.sendto(data, address_data_channel)
    print('[data] sent')

    time.sleep(1)
    count += 1
