import threading
import queue
import bluetooth
from time import sleep
import os
import socket

class BluetoothSocket(threading.Thread):
    """Bluetooth Reader class that provides an interface to read from a
        bluetooth port and write to a queue on a separate threadself.
        Arguments: targetName{string} the bluetooth name of module
                   q{queue.Queue object} the queue to write"""
    def __init__(self, targetName, dataqueue):

        super(BluetoothSocket, self).__init__()
        self.q = dataqueue

         # Defines module name and its MAC address
        self.targetName = targetName
        self.targetAddress = None

        # Exceptions aren't thrown from threads to an interface has to be made to get the errors
        self.exception = None

    def connect(self):
        # Searches for module name in nearby bluetooth services
        # nearby_devices = bluetooth.discover_devices()
        # print(nearby_devices)

        try:
            self.target_address = '00:14:03:06:73:A0'
            self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.connect((self.target_address, 1))
            print("And it has just been connected.")
        except Exception as e:
            print(e)
            print("Can't connect for some reason.")
            print("Make sure bluetooth is turned on. Or try restarting it.")
            raise(e)

    def receiveData(self):
        self.currDataArray = []

        # Reads and decodes data received from Bluetooth socket
        bytes = self.sock.recv(1024)
        parsedString = bytes.decode("utf-8")
        #print(parsedString)

        # Manipulates data into specific datapoints for plotting
        # with '-' being used as delimiter between datapoints
        try:
            lastPos = parsedString.rfind("-")
            if(lastPos != -1):
                self.currData = self.lastData + parsedString[0:lastPos]
                self.lastData = parsedString[lastPos+1:]
                self.currDataArray = self.currData.split('-')
            else:
                self.lastData = parsedString
        except:
                pass
        # print(self.currDataArray)
        return self.currDataArray

    def run(self):
        self.currData = ""
        self.lastData = ""

        # Establishes connection with module
        self.connect()

        # Constantly checks for new data and writes to queue
        try:
            while True:
                for datapoints in self.receiveData():
                    try:
                        if(datapoints != ''):
                            self.q.put([float(x) for x in datapoints.split('/') ])
                    except:
                        print('Error:', datapoints)
        except:
            self.sock.close()

    def get_exception(self):
        return self.exception

class LocalSocket:
    def __init__(self,q):
        super(LocalSocket, self).__init__()
        self.queue = q
        print("starting local socket")
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Done")
        self.port = 12345
        self.lastdata = 0

    def connect(self):
        print("binding")
        self.s.bind(('127.0.0.1', self.port))
        print("waiting for connections")
        self.s.listen(5)
        self.c, addr = self.s.accept()
        print("accepted connection")
        self.c.settimeout(30)
        self.c.send("1.0,1.0,1.0,1.0 \n".encode('ascii'))
        return self.c

    def startTransfer(self):
        print(self.c)
        while True:
            sleep(0.01)
            try:
                self.lastdata = self.queue.get(block=False)
                self.c.send((str(self.lastdata)[1:-1] +'' '\n').encode('ascii'))
                # print(self.queue.qsize())
                print(repr(str(self.lastdata)[1:-1] +'' '\n').encode('ascii'))
            except queue.Empty:
                self.c.send((str(self.lastdata)[1:-1] +'' '\n').encode('ascii'))
                continue;
            except Exception as e:
                self.c.close()
                print(self.c)
                print(e)
                break;

if __name__ == '__main__':

    # Initialise the queue where data will be stored
    dataqueue = queue.Queue()

    # Initialises LocalSocket and BluetoothModule and set it to kill program if only it is left (when main thread dies)
    s = LocalSocket(dataqueue)

    targetName = "The SmartGlove"
    reader = BluetoothSocket(targetName, dataqueue)
    reader.daemon = True

    # Main logic
    reader.start()
    s.connect()

    s.startTransfer()
