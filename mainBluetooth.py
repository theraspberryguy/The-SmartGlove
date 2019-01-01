import threading
import queue
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as tkr
import argparse
import bluetooth
from time import sleep
import os

class BluetoothModule(threading.Thread):
    """Bluetooth Reader class that provides an interface to read from a
        bluetooth port and write to a queue on a separate threadself.
        Arguments: targetName{string} the bluetooth name of module 
                   q{queue.Queue object} the queue to write"""
    def __init__(self, targetName, dataqueue):

        super(BluetoothModule, self).__init__()
        self.q = dataqueue

         # Defines module name and its MAC address
        self.targetName = targetName
        self.targetAddress = None

        # Exceptions aren't thrown from threads to an interface has to be made to get the errors
        self.exception = None

    def connect(self):
        # Searches for module name in nearby bluetooth services        
        nearby_devices = bluetooth.discover_devices()
        
        for addr in nearby_devices:
            if self.targetName == bluetooth.lookup_name( addr ):
                self.target_address = addr
                break

        # User feedback to show if connected to module
        if self.target_address is not None:
            print("Your glove has been detected with address ", self.target_address, ".")
        else:
            print ("Could not find your glove nearby.")

        try:
            #self.target_address = '00:06:66:EC:00:8F'
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
        print(parsedString)

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
        while True: 
            for datapoints in self.receiveData():
                try:
                    if(datapoints != ''):
                        self.q.put([float(x) for x in datapoints.split('/') ])
                except:
                    print('Error:', datapoints)

    def get_exception(self):
        return self.exception

class Plotter:
    """Plotter class that encapsulates all the necessary methods to make pyplots easy to use
        Args: Queue object that represents incoming data queue
              maxLength: Length of x-axis and data
    """
    def __init__(self, queue, maxLength, numSensors):
        self.Paused = False
        self.maxLength = maxLength
        self.queue = queue
        self.numSensors = numSensors
        #  set up the graph and axes and do a bunch of formatting
        self.fig = plt.figure()
        self.axes = plt.axes(xlim=(0,self.maxLength), ylim=(0.0,3.4))
        self.axes.yaxis.tick_right()
        self.axes.yaxis.set_major_locator(tkr.LinearLocator(numticks=10))
        self.axes.yaxis.set_minor_locator(tkr.AutoMinorLocator())

        # Dynamic number of sensors
        self.sensorData = [[0.0]*self.maxLength]*self.numSensors
        self.sensors = []

        # Mulitple graphs setup
        for x in range(0,self.numSensors):
            self.sensor, = self.axes.plot(range(self.maxLength),self.sensorData[x])
            self.sensors.append(self.sensor)

        self.cid = self.fig.canvas.mpl_connect('key_press_event', self.OnSpace)

    # This function updates the graph every time FuncAnimation calls it

    def update(self, i):
        if self.Paused:
            return (x for x in self.sensors)
        # Get (and remove) first item in queue
        datalist = self.queue.get()
        try:
            # Plot the new data
            for x in range(0,self.numSensors):
                 self.sensorData[x] = self.sensorData[x][1:] + [datalist[x]*3.3]
                 self.sensors[x].set_data(range(self.maxLength), self.sensorData[x])
        except Exception as e:
            print(str(e))
        # Return the portions of the graph that have changed in order to blit
        return (x for x in self.sensors)

    # Function that is called on spacebar pressed
    def OnSpace(self, event):
        if event.key == ' ':
            self.Paused = not self.Paused
            if not self.Paused:
                with self.queue.mutex:
                    self.queue.queue.clear()



if __name__ == '__main__':

    # Initialise the queue where data will be stored
    dataqueue = queue.Queue()

    # Initialise SerialReader and set it to kill program if only it is left (when main thread dies)
    targetName = "RNBT-008F"
    reader = BluetoothModule(targetName, dataqueue)
    reader.daemon = True
    print("Starting...")
    reader.start()

    # Initialise plotter class
    maxLength = 100
    numSensors = 6
    plot = Plotter(dataqueue, maxLength, numSensors)

    # define the animation to run (calls plot.update every 1 ms with blitting)
    anim = animation.FuncAnimation(plot.fig, plot.update, interval=1, blit=True)


    print("Initialised plot")

    # start the actual plot
    plt.show()

    #clear up all the io buffers and close port
    reader.sock.close()
