import sys
import json
import time
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
    'uid': sys.argv[1]
}
clientSocket.send('{}\n'.format(json.dumps(data_login)).encode('utf-8'))

with clientSocket.makefile() as f:
    for line in f:
        line = line.rstrip()
        if len(line) == 0:
            break
        print('{} {}'.format(len(line), line))
