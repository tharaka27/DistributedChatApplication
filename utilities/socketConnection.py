import socket
from queue import Queue
from utilities.executor_pool import Executor_pool

# import thread module
from _thread import *
import threading

def exception_handler(thread_name, exception):
    print(f'{thread_name}: {exception}')
    
#Server side socket class
class Socket(object):
    def __init__(self, host, port, exception_handler=exception_handler):
        self.host   = host
        self.port  = port
        self.queue = Queue()
        self.pool = Executor_pool(name='Pool_1', queue=self.queue, max_workers=4, wait_queue=False, exception_handler=exception_handler)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.bind((self.host,self.port))
        print(f"Socket binded to port {self.port}")

    
    # thread function
    def threaded(self, client):
        while True:
    
            # data received from client
            data = client.recv(1024)
            if not data:
                print('Bye')
                break
    
            # reverse the given string from client
            data = data[::-1]

            ## todo: read data request
            ## todo: write response data

            # send back reversed string to client
            client.send(data)
    
        # connection closed
        client.close() 

    # Listen for requests 
    def listen(self, backlog=5):
        self.socket.listen(backlog)
        print(f"Listening on {self.port}")

        # Keep serving requests
        self.running = True

        # a forever loop until client wants to exit
        while self.running:
            # establish connection with client
            client, address = self.socket.accept()
            print(f'Connected to :{address[0]}:{address[1]}')
    
            # task is a tuple of a function, args and kwargs.
            task = threading.Thread(target = self.threaded, args = (client, ))
            self.queue.put(task)

            # todo: implement break condition for the while loop

        self.socket.close()
    
    def start(self):
        try:
            # start the Pool
            self.pool.start()
            # go back to the main thread from time to another to check the KeyboardInterrupt
            while self.is_alive():
                self.join(0.5)

        except (KeyboardInterrupt, SystemExit):
            # shutdown the pool by aborting its Workers/threads.
            self.shutdown()


s = Socket("localhost",8000)
