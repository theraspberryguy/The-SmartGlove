import math
import matplotlib.animation as anim
import matplotlib.image as mplimg
from matplotlib.patches import Circle
import numpy as np
import matplotlib.pyplot as plt
import argparse
import NewThreading as serialreader
import queue
print("started")

Paused = False


def beginparser():
    """
    Makes a new instance of ArgumentParser and then adds the required command line Arguments
    Return type dictionary of arguments
    """
    parser = argparse.ArgumentParser(description="SerialPlotter")
    parser.add_argument('--port', dest='port', required=True)
    parser.add_argument('--baud', dest='baudrate', required=True, type=int)
    parser.add_argument('--len', dest='maxLength', default=100, type=int)
    args = parser.parse_args()
    return args


args = beginparser()

# Initialise the queue where data will be stored
dataqueue = queue.Queue()

# Initialise SerialReader and set it to kill program if only it is left (when main thread dies)
reader = serialreader.SerialReader(args.port, args.baudrate, dataqueue)
reader.daemon = True
print("Starting Thread....")
reader.start()

image_file = 'hand.png'
img = plt.imread(image_file)


# Create a figure. Equal aspect so circles look circular
fig, ax = plt.subplots(1)
ax.set_aspect('equal')

# Show the image
ax.imshow(img)

# Create two circles for each finger and dump them on the hand
circ1 = Circle((747, 761), 100, color=(1, 1, 0))
circ2 = Circle((700, 490), 100, color=(1, 1, 0))
ax.add_patch(circ1)
ax.add_patch(circ2)

# Define the function that is called every time the graph updates


def update(i):
    global Paused
    if Paused:
        return circ1, circ2
    # Monitor Queue size
    print(dataqueue.qsize())
    # Get (and remove) first item in queue
    datalist = dataqueue.get()
    try:
        # Append the new data to the list and remove the oldest value
        circ1.set_color((1, datalist[0], 0))
        circ2.set_color((1, datalist[1], 0))
        # Plot the new data
    except Exception as e:
        print(str(e))
    # return the portions of the graph that have changed in order to blit
    return circ1, circ2


# Hide axis
plt.axis('off')

# Start animation
animation = anim.FuncAnimation(
    fig, update, interval=1, blit=True)


# Set up pausing
def OnSpace(event):
    global Paused
    if event.key == ' ':
        Paused = not Paused
        if not Paused:
            with dataqueue.mutex:
                dataqueue.queue.clear()


cid = fig.canvas.mpl_connect('key_press_event', OnSpace)

# Show the image
plt.show()

# Clean up when everything quits
reader.conn.flush()
reader.conn.reset_input_buffer()
reader.conn.close()
