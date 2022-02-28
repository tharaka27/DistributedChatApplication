import time
import threading
import random
from testcases import test_threadpool, test_chatroominfo

def main():
    test_threadpool.test()
    test_chatroominfo.test()


if __name__ == "__main__":
    main()