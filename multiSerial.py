from NewThreading import SerialReader
from mainBluetooth import Plotter



def beginparser():
    """
    Makes a new instance of ArgumentParser and then adds the required command line Arguments
    Return type dictionary of arguments
    """
    parser = argparse.ArgumentParser(description="SerialPlotter")
    parser.add_argument('--port', dest='port', default='COM3')
    parser.add_argument('--baud', dest='baudrate', default=115200, type=int)
    parser.add_argument('--len', dest='maxLength', default=100, type=int)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = beginparser()

    # Initialise the queue where data will be stored
    dataqueue = queue.Queue()

    # Initialise SerialReader and set it to kill program if only it is left (when main thread dies)
    reader = SerialReader(args.port, args.baudrate, dataqueue)
    reader.daemon = True
    print("Starting Thread....")
    reader.start()

    # Initialise plotter class
    plot = Plotter(dataqueue, args.maxLength)

    # define the animation to run (calls plot.update every 1 ms with blitting)
    anim = animation.FuncAnimation(
        plot.fig, plot.update, interval=1, blit=True)

    print("Initialised plot")

    # start the actual plot
    plt.show()

    print("exiting")

    # clear up all the io buffers and close port
    reader.conn.flush()
    reader.conn.reset_input_buffer()
    reader.conn.close()
