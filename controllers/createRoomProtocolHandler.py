from models import serverstate 
from models.userSession import UserSession
from models.localroominfo import LocalRoomInfo
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.bully import Bully 
import json
import time

class createRoomProtocolHandler:
    def __init__(self, identity, json_data):
        self._protocol = "createroom"
        self._identity = identity
        self._roomid = json_data["roomid"]
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        self._local_server_name = serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
        
    def handle(self):
        print("[INFO] Handling create room request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._roomid, self._message_builder.coordinatorNotAlive(self._protocol)

        # check whether I am coordinator
        if serverstate.AMICOORDINATOR:
            print("[INFO] Handling new identity inside AMICOORDINATOR.")
            
            # the room exists
            isRoomExist = False
            for room in serverstate.ALL_CHAT_ROOMS:
                if room.getId == self._roomid:
                    isRoomExist = True
                    
            if isRoomExist :
                return self._roomid, self._message_builder.newChatRoom(self._roomid,"False")

            else:
                # create new chat room instance
                chat_room_instance = LocalRoomInfo()
                chat_room_instance.setChatRoomID(self._roomid)
                chat_room_instance.setOwner(self._identity)
                chat_room_instance.setCoordinator(self._local_server_name)

                # add to the local chat rooms list
                serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)

                # add to the global chat room list
                serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)
                return self._roomid, self._message_builder.newChatRoom(self._roomid,"True") 

        else:
            # forward the message to the coordinator
            print("[INFO] Forwarding the create_identity request to coordinator")
            message = { "type" : "create_chat_room" , "identity" : self._identity,\
                 "server": self._local_server_name, "roomid" : self._roomid}
            
            self._bully_instance.send_buffer.append(message)

            while(len(self._bully_instance.receive_buffer) == 0):
                time.sleep(1)
            
            print("[Received]", end="")
            message = json.loads(self._bully_instance.receive_buffer.pop(0))
            print(type(message))
            
            try:
                if message["approved"] == "True" :
                    print("csss")
                    
                    # create new chat room instance
                    chat_room_instance = LocalRoomInfo()
                    chat_room_instance.setChatRoomID(self._roomid)
                    chat_room_instance.setOwner(self._identity)
                    chat_room_instance.setCoordinator(self._local_server_name)

                    # add to the local chat rooms list
                    serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)

                    # add to the global chat room list
                    serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)
                    print("Camee here")
                    return self._roomid, self._message_builder.newChatRoom(self._roomid,"True")  
                else:
                    print("Camee here2")
                    return self._roomid, self._message_builder.newChatRoom(self._roomid,"False") 
            except Exception as e :
                print(e)