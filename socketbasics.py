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
    x = 0.3
    try:
        v = mill() - t
        a = math.sin((v/100)+x)
        b = math.sin((v/100)+x*2)
        _c = math.sin((v/100)+x*3)
        d = math.sin((v/100)+x*4)
        e = math.sin((v/100)+x*5)
        f = math.sin((v/100)+x*6)
        c.send((str(a) + ',' + str(b) + ','+ str(_c) + ','+ str(d) + ','+ str(e) + ','+ str(f) + '\n').encode('ascii'))
        time.sleep(0.001)
    except Exception as e:
        print(e)
        c.close()
        break;
