from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
import json
import time

class whoProtocolHandler:
    def __init__(self, roomid):
        self._protocol = "who"
        self._roomid = roomid
        self._bully_instance = FastBully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling who request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        identites = []

        owner = ""
        try:
            for room in serverstate.LOCAL_CHAT_ROOMS:
                if room.getChatRoomId() == self._roomid:
                    owner = room.getOwner()
                    identites = room.getMembers()
            
        except Exception as e:
            print(e)
        return self._message_builder.whoProtocol(self._roomid, identites, owner )

        

        