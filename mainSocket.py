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
        '''nearby_devices = bluetooth.discover_devices()

        for addr in nearby_devices:
            if self.targetName == bluetooth.lookup_name( addr ):
                self.target_address = addr
                break

        # User feedback to show if connected to module
        if self.target_address is not None:
            print("Your glove has been detected with address ", self.target_address, ".")
        else:
            print ("Could not find your glove nearby.")'''

        try:
            self.target_address = '00:14:03:06:73:A0'
            self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            self.sock.connect((self.target_address, 1))
            print("And it has just been connected.")
        except:
            print("Can't connect for some reason.")
            print("Make sure bluetooth is turned on. Or try restarting it.")

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

        self.s = socket.socket()
        self.port = 12345

    def connect(self):
        self.s.bind(('127.0.0.1', self.port))
        self.s.listen(5)
        self.c, addr = self.s.accept()
        self.c.settimeout(30)
        #self.c.send("helloWorld".encode('utf-8'))
        return self.c

    def startTransfer(self):
        while True:
            try:
                datalist = self.queue.get()
                self.c.send(str(datalist).encode('utf-8'))
                print(datalist)
            except:
                self.c.close()

if __name__ == '__main__':

    # Initialise the queue where data will be stored
    dataqueue = queue.Queue()

    # Initialises LocalSocket and BluetoothModule and set it to kill program if only it is left (when main thread dies)
    s = LocalSocket(dataqueue)

    targetName = "The SmartGlove"
    reader = BluetoothSocket(targetName, dataqueue)
    reader.daemon = True
    print("started module")

    # Main logic
    print("started stuff")
    s.connect()
    print("finished connecting")
    reader.start()
    s.startTransfer()
