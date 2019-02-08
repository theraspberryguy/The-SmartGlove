import time
import socket
import math


mill = lambda: int(round(time.time()*1000))

t = mill()
s = socket.socket()

s.bind(('127.0.0.1', 12345))

s.listen(5)

c, addr = s.accept()

c.settimeout(30)


while True:
    try:
        v = mill() - t
        a = math.sin(v/100)
        c.send((str(a) + ', 1.0' + ', 0.5' '\n').encode('ascii'))
        print(round(a, 3))
        time.sleep(0.01)
    except Exception as e:
        c.close()
        break;
