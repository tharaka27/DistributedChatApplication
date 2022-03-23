from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import Bully 
from models.localroominfo import LocalRoomInfo
import json
import time

class moveJoinProtocolHandler:
    def __init__(self,identity, current_room,json_data):
        self._protocol = "movejoin"
        self._next_room = json_data["roomid"]
        self._identity = identity
        self._current_room = current_room
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):

        print("[INFO] Handling new identity request started.")
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        #checks in local rooms weather the room exists
        for r in serverstate.LOCAL_CHAT_ROOMS:

            room_id = r.getChatRoomId()

            if room_id == self._next_room :
                # room exists
                serverstate.LOCAL_USERS.append(self._identity)
                r.addMember(self._identity)
                return True,self._message_builder.serverChange("true")
        
        # if room is not found -> places in main hall
        hallname = "MainHall-" + serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
        for r in serverstate.LOCAL_CHAT_ROOMS:

            room_id = r.getChatRoomId()

            if room_id == hallname :
                # room exists
                serverstate.LOCAL_USERS.append(self._identity)
                r.addMember(self._identity)
                return False,self._message_builder.roomChange(self._identity,self._current_room,hallname)
        









                    

        
        