from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
from models.localroominfo import LocalRoomInfo
import json
import time

class joinRoomProtocolHandler:
    def __init__(self,identity, current_room,json_data):
        self._protocol = "joinroom"
        self._next_room = json_data["roomid"]
        self._identity = identity
        self._current_room = current_room
        self._bully_instance = FastBully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):

        print("[INFO] Handling joinroom request started.")
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        current_room_instance = LocalRoomInfo()
        # check weather identity is the admin in current room
        for r in serverstate.LOCAL_CHAT_ROOMS:
            room_id = r.getChatRoomId()
            if room_id == self._current_room:
                
                current_room_instance = r

                admin = r.getOwner()
                if admin == self._identity :
                    # identity is the current owner therefore cannot go to room
                    return "n",self._message_builder.roomChange(self._identity,self._current_room,self._current_room)
                else:
                    # not the admin in current room can move
                    print("[INFO] Not the admin in current room can move")
                    break


        # check weather the reuested room in local server
        for r in serverstate.ALL_CHAT_ROOMS:

            room_id = r.getChatRoomId()

            if room_id == self._next_room:

                r_cod = r.getCoordinator()
                if r_cod == serverstate.LOCAL_SERVER_CONFIGURATION.getServerName():
                    #room found in same server
                    print(current_room_instance.getMembers())
                    current_room_instance.removeMember(self._identity)
                    r.addMember(self._identity)
                    return "b",self._message_builder.roomChange(self._identity,self._current_room,self._next_room)
                
                else:
                    #room found in a remote server
                    print("room in a remote server")
                    current_room_instance.removeMember(self._identity)
                    print("remove from existing room")
                    serverstate.LOCAL_USERS.remove(self._identity)
                    print("remove from local users")
                    host = ""
                    port = ""
                    for s in serverstate.REMOTE_SERVER_CONFIGURATIONS:

                        s_name = s.getServerName()
                        print(s_name,r_cod)
                        if s_name == r_cod:
                            host = s.getAddress()
                            port = s.getClientPort()
                            return "o",self._message_builder.route(self._next_room,host,port)
        
        # not found in rooms -> room does not exist
        return "n",self._message_builder.roomChange(self._identity,self._current_room,self._current_room)






                    

        
        