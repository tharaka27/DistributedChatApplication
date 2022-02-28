import time
import threading
import random
from testcases import test_threadpool, test_chatroominfo , test_configuration, test_localroominfo, test_remoteroominfo

def main():
    #test_threadpool.test()
    #test_chatroominfo.test()
    #test_configuration.test()
    #test_localroominfo.test()
    test_remoteroominfo.test()


if __name__ == "__main__":
    main()