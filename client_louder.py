import sys
import time
import json
from socket import *

HOST = '127.0.0.1'
PORT = 10000
BUFSIZE = 1024
ADDR = (HOST, PORT)

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)
except ConnectionError as e:
    print('채팅 서버(%s:%s)에 연결 할 수 없습니다.' % ADDR)
    sys.exit()

data_login = {
    'code': 1000,
    'app_id': 'app1',
    'uid': 'user1'
}
clientSocket.send('{}\n'.format(json.dumps(data_login)).encode('utf-8'))

data = clientSocket.recv(BUFSIZE)
print(data.decode('utf-8'))

keyword = sys.argv[1]
count = 0

while True:
    line = '{}{}\n'.format(keyword, count)
    clientSocket.send(line.encode('utf-8'))
    print('sent')
    time.sleep(1)
    count += 1
