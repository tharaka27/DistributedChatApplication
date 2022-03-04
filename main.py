import time
import threading
import random
from testcases import test_threadpool, test_chatroominfo , test_configuration, test_localroominfo, test_remoteroominfo, test_fileReader

def main():
    #test_threadpool.test()
    #test_chatroominfo.test()
    #test_configuration.test()
    #test_localroominfo.test()
    #test_remoteroominfo.test()
    test_fileReader.test()


if __name__ == "__main__":
    main()