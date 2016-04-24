import sys
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


data = clientSocket.recv(BUFSIZE)
print(data.decode('utf-8'))

keyword = sys.argv[1]

while True:
    line = '{}\n'.format(keyword)
    clientSocket.send(line.encode('utf-8'))
    print('sent')
    time.sleep(1)
