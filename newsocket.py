import time
import socket
import math
import mainSocket
import queue

dataqueue = queue.Queue()

# Initialise SerialReader and set it to kill program if only it is left (when main thread dies)
targetName = "The SmartGlove"
reader = mainSocket.BluetoothSocket(targetName, dataqueue)
reader.daemon = True
print("Starting...")
reader.start()

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
        data = dataqueue.get(False)
        pass

    except queue.Empty:
        pass

    try:
        v = mill() - t
        # print()
        a = math.sin((v/100)+x)
        b = math.sin((v/100)+x*2)
        _c = math.sin((v/100)+x*3)
        d = math.sin((v/100)+x*4)
        e = math.sin((v/100)+x*5)
        f = math.sin((v/100)+x*6)
        # c.send((str(a) + ' ,' + str(b) + ' ,'+ str(_c) + ' ,'+ str(d) + ' ,'+ str(e) + ' ,'+ str(f) + ' \n').encode('ascii'))
        c.send((str(data)[1:-1] +'' '\n').encode('ascii'))
        print(("REal" + str(data)[1:-1] +'' '\n').strip().encode('ascii'))
        # print(("Test" + str(a) + ' ,' + str(b) + ' ,'+ str(_c) + ' ,'+ str(d) + ' ,'+ str(e) + ' ,'+ str(f) + ' \n').encode('ascii'))
        # time.sleep(0.01)
    
    except Exception as e:
        print(e)
        print("Exception    ")
        c.close()   
        break
