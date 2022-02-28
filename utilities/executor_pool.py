import os
#from executor import exception_handler, Executor
from .executor import Executor, exception_handler 
from queue import Queue, Empty
import threading
import time

class Executor_pool:
    def __init__(self, max_workers=os.cpu_count()+2, name=None, queue=None,\
        wait_queue=True, result_queue=None, workers_sleep=0.5, callback=None, \
            exception_handler=exception_handler):
            self.name           = name
            self.max_workers    = max_workers
            self.callback       = callback
            self.workers_sleep  = workers_sleep
            self.exception_handler  = exception_handler

            self.queue          = queue if isinstance(queue, Queue) else Queue()
            self.result_queue   = result_queue if isinstance(result_queue, Queue) else Queue()
            self.wait_queue     = wait_queue

            self.threads        = []


    def start(self):
        #reinitialize values
        self.threads = []

        #create all threads
        for i in range(self.max_workers):
            self.threads.append(Executor(f'Worker_{i}_{self.name}', self.queue, \
                self.result_queue, wait_queue=self.wait_queue, sleep=self.workers_sleep,\
                    callback=self.callback))
        
        for t in self.threads:
            t.start()

        return True

    def is_alive(self):
        return any((t.is_alive() for t in self.threads))
    
    def is_idle(self):
        return False not in (t.idle() for t in self.threads)

    def is_done(self):
        return self.queue.empty()
    
    def shutdown(self, block=False):
        # Abort all the threads in the pool
        for t in self.threads:
            t.resume() # the thread should be working to abort it.
            t.abort()
        self.block(block)
        self.result_queue = None

    def join(self, timeout=None):
        # wait until all the queue tasks be completed
        if timeout and self.is_alive():
            time.sleep(timeout)
        else:
            self.queue.join()
        
    def result(self, block=False):
        # return results as a generator
        result = []
        if block and self.is_alive():
            self.join()
        
        try:
            while True:
                result.append(self.result_queue.get(False))
                self.result_queue.task_done()
        
        except:
            # the result_queue is empty
            pass

        return result
    
    def __del__(self):
        self.shutdown()

    def is_paused(self):
        return False not in ( t.paused() for t in self.threads)

    def pause(self, timeout=0, block=False):
        for t in self.threads:
            t.pause()
        if timeout:
            time.sleep(timeout)
            self.resume()
        return True
    
    def resume(self, block=True):
        for t in self.threads:
            t.resume()
        return True
    
    def block(self, block=True):
        while block and self.is_alive():
            time.sleep(0.5)

    def count(self):
        return len(self.threads)
    
    def update(self, n, block=False):
        # create necessary threads
        need = n - self.count()
        if need > 0:
            # create more threads
            t = Executor(f'Worker_{self.count()}_{self.name}', self.queue, \
                self.result_queue, wait_queue=self.wait_queue, sleep=self.workers_sleep,\
                    callback=self.callback)
            t.start()
            self.threads.append(t)

        elif need < 0:
            need = abs(need)
            # delete some threads
            threads = []
            for _ in range(need):
                t = self.threads.pop()
                t.resume() # the thread should be working to abort it.
                t.abort()
                threads.append(t)

            # block until the extra threads dead.
            while block and any(( t.is_alive() for t in threads)):
                time.sleep(0.5)
    


        
