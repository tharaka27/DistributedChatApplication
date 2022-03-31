from models.chatroominfo import ChatRoomInfo
import threading

class LocalRoomInfo (ChatRoomInfo):

    def __init__(self, ChatRoomId="" ,owner="",  coordinator=""):
        #self.lock = threading.Lock()
        self.setChatRoomID(ChatRoomId)
        self.owner = owner
        self.members = []
        self.coordinator = coordinator

    def getOwner(self):
        return self.owner
    
    def setOwner(self,owner):
        self.owner = owner

    def addMember(self,identity):
        #self.lock.acquire()
        try:
            self.members.append(identity)
        finally:
            #self.lock.release()
            pass

    def removeMember(self,identity):
        #self.lock.acquire()
        try:
            self.members.remove(identity)
        finally:
            #self.lock.release()
            pass
    
    def getMembers(self):
        #self.lock.acquire()
        try:
            return self.members
        finally:
            #self.lock.release()
            pass

    def setCoordinator(self, coordinator):
        self.coordinator = coordinator

    def getCoordinator(self):
        return self.coordinator
    
    def setMembers(self,member_list):
        #self.lock.acquire()
        try:
            self.members = member_list
        finally:
            #self.lock.release()
            pass

    