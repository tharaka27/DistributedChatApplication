import time
import threading
import random

from queue import Queue
from utilities.executor_pool import Executor_pool

# Our logic to be performed Asynchronously.
def our_process(a):
	t = threading.current_thread()
	# just to semulate how mush time this logic is going to take to be done. 
	time.sleep(random.uniform(0, 3))
	print(f'{t.getName()} is finished the task {a} ...')


# Our function to handle thrown exceptions from 'our_process' logic.
def exception_handler(thread_name, exception):
    print(f'{thread_name}: {exception}')


def test():
    # create a queue & pool.
    q = Queue()
    p = Executor_pool(name='Pool_1', queue=q, max_workers=4, wait_queue=False, exception_handler=exception_handler)

    # adding some tasks the the queue.
    for i in range(10):
        # task is a tuple of a function, args and kwargs.
        our_task = (our_process, (i,), {})
        q.put(our_task)

    try:
        # start the Pool
        p.start()
        # go back to the main thread from time to another to check the KeyboardInterrupt
        while p.is_alive():
            p.join(0.5)

    except (KeyboardInterrupt, SystemExit):
        # shutdown the pool by aborting its Workers/threads.
        p.shutdown()
