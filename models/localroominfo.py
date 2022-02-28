from models.chatroominfo import ChatRoomInfo
import threading

class LocalRoomInfo (ChatRoomInfo):

    def __init__(self, owner=""):
        self.lock = threading.Lock()
        self.owner = owner
        self.members = []

    def getOwner(self):
        return self.owner
    
    def setOwner(self,owner):
        self.owner = owner

    def addMember(self,identity):
        self.lock.acquire()
        try:
            self.members.append(identity)
        finally:
            self.lock.release()

    def removeMember(self,identity):
        self.lock.acquire()
        try:
            self.members.remove(identity)
        finally:
            self.lock.release()
    
    def getMembers(self):
        self.lock.acquire()
        try:
            return self.members
        finally:
            self.lock.release()



    