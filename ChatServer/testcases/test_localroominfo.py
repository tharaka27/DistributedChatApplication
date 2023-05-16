from models.localroominfo import LocalRoomInfo
import threading

def worker1(local):

    members = ["vihan","tharaka","shafeek","zameel"]

    for i in range(0,4):
        local.addMember(members[i])

def worker2(local):

    local.addMember("krishi")
    local.addMember("denuwan")
        

def test():

    local = LocalRoomInfo()
    local.setChatRoomID("chatroom 1")
    local.setOwner("vihan")

    t1 = threading.Thread(target=worker1, args=(local,))
    t2 = threading.Thread(target=worker2, args=(local,))
    t1.start()
    t2.start()

    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()
    
    print(local.getChatRoomId())
    print(local.getOwner())
    print(local.getMembers())