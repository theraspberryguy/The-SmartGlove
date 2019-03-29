import time
import socket
import math


mill = lambda: int(round(time.time()*1000))

t = mill()
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(('127.0.0.1', 12345))

s.listen(5)

c, addr = s.accept()

c.settimeout(30)

for i in range(100):
    try:
        v = mill() - t
        a = math.sin(v/100)
        c.send((str(i) + ', 1.0' + ', 0.5' + '\n').encode('ascii'))
        print(repr(str(a) + ', 1.0' + ', 0.5' + '\n').encode('ascii'))
        time.sleep(0.01)
    except Exception as e:
        c.close()
        break;

# time.sleep(1.5);

while True:
    try:
        v = mill() - t
        a = math.sin(v/100)
        c.send((str(a) + ', 1.0' + ', 0.5 ,' +  str(a/10) + ',' + str(a*5) + '\n').encode('ascii'))
        print(repr(str(a) + ', 1.0' + ', 0.5' + '\n').encode('ascii'))
        time.sleep(0.01)
    except Exception as e:
        c.close()
        break;
