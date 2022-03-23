from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import Bully 
from models.localroominfo import LocalRoomInfo
import json
import time

class deleteRoomProtocolHandler:
    def __init__(self,identity,json_data):
        self._protocol = "deleteroom"
        self._delete_room = json_data["roomid"]
        self._identity = identity
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):

        print("[INFO] Handling new identity request started.")
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        #checks in all rooms weather the room exists
        for r in serverstate.ALL_CHAT_ROOMS:

            r_id = r.getChatRoomId()
            if r_id == self._delete_room:
                r_owner = r.getOwner()
                if r_owner == self._identity :
                    # can delete the room
                    print("delete room")

                else:
                     # cannot delete the room
                    return False,self._message_builder.deleteRoom(self._delete_room,"false")
        
        # room does not exist cannot delete room
        return False,self._message_builder.deleteRoom(self._delete_room,"false")







                    

        
        