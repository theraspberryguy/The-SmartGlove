import mainSocket
import threading
import random
import time
import queue

class Pipe(threading.Thread):
    """docstring for Pipe."""
    def __init__(self, queue):
        super(Pipe, self).__init__()
        self.queue = queue

    def run(self):
        while True:
            a = str(random.randint(0, 100))
            self.queue.put(a + '\n')
            print(a)
            time.sleep(0.1)


queue = queue.Queue()
pipe = Pipe(queue)
pipe.daemon = True
# pipe.start()

s = mainSocket.LocalSocket(queue)

print("started stuff")
s.connect()
print("finished connecting")
pipe.start()
s.startTransfer()
