from queue import Queue, Empty
import os
import threading
import time

def exception_handler(thread_name, exception):
    print(f'{thread_name}: {exception}')

class Executor(threading.Thread):
    def __init__(self, name, queue, result=None, wait_queue=False, sleep=0.5,\
        callback=None, exception_handler=exception_handler):

        threading.Thread.__init__(self)
        self.name   = name
        self.queue  = queue
        self.result = result if isinstance(result, Queue) else Queue()
        self.sleep  = sleep
        self._abort = threading.Event()
        self._idle  = threading.Event()
        self._pause = threading.Event()
        self.wait_queue = wait_queue
        self.exception_handler = exception_handler
        self.callback = callback
    
    def abort(self, block=True):
        self._abort.set()
        self.block(block)

    def aborted(self):
        return self._abort.is_set()

    def pause(self):
        self._pause.set()
        self._idle.set()

    def resume(self):
        self._pause.clear()
        self._idle.clear()

    def paused(self):
        self._pause.is_set()

    def __del__(self):
        if not self.aborted():
            self.abort()
    
    def _pause_now(self):
        while self.paused():
            time.sleep(self.sleep)

    def block(self, block=True):
        while block and self.is_alive():
            time.sleep(self.sleep)
    
    def run(self):
        while not self.aborted():
            try:
                func, args, kwargs = self.queue.get(timeout=0.5)
                self._idle.clear()
            except Empty:
                #queue is empty
                self._idle.set()
                #abort the thread if queue is empty
                if not self.wait_queue:
                    break
                continue
            except Exception as e:
                pass

            # the task is available to work with
            try:
                r = func(*args, **kwargs)
                self.result.put(r)
                if self.callback:
                    self.callback(r)
            
            except Exception as e:
                self.exception_handler(self.name, e)
            finally:
                self.queue.task_done()
            
            # pause the thread is _pause flag is set
            self._pause_now()