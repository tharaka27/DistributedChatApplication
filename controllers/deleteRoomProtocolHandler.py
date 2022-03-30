from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
from models.localroominfo import LocalRoomInfo
import json
import time

class deleteRoomProtocolHandler:
    def __init__(self,identity,json_data):
        self._protocol = "deleteroom"
        self._delete_room = json_data["roomid"]
        self._identity = identity
        self._bully_instance = FastBully._instance
        self._message_builder = MessageBuilder._instance
        self._serverid = serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
        
    def handle(self):

        print("[INFO] Handling delete request started.")
        # check whether coordinator is alive

        mainHallName =  "MainHall-" + self._serverid

        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        #checks in all rooms weather the room exists
        for r in serverstate.LOCAL_CHAT_ROOMS:

            r_id = r.getChatRoomId()
            if r_id == self._delete_room:
                r_owner = r.getOwner()
                if r_owner == self._identity :
                    # can delete the room
                    # check whether I am coordinator
                    if serverstate.AMICOORDINATOR:
                        print("[INFO] Handling delete inside AMICOORDINATOR.")

                        # move users from current to mainhall
                        members = r.getMembers()
                        for hall in serverstate.LOCAL_CHAT_ROOMS:

                            h_id = hall.getChatRoomId()

                            if h_id == mainHallName:

                                for m in members:
                                    hall.addMember(m)
                        
                        # remove the room
                        serverstate.ALL_CHAT_ROOMS.remove(r)
                        serverstate.LOCAL_CHAT_ROOMS.remove(r)

                        try:
                            self._bully_instance.task_list.append({"type" : "deleteroom","serverid": self._serverid,"roomid":self._delete_room})
                            return True,members,self._message_builder.deleteRoom(self._delete_room,"true")
                        except :
                            print("[Error] Error occured while distributing the delete room")

                        print("[INFO] FINISHED")
                    
                    else:

                        # forward the message to the coordinator
                        print("[INFO] Forwarding the deleteroom request to coordinator")


                        message = {"type" : "deleteroom","serverid": self._serverid,"roomid":self._delete_room}
                        
                        self._bully_instance.send_buffer.append(message)

                        while(len(self._bully_instance.receive_buffer) == 0):
                            time.sleep(1)
                        
                        print("[Received]", end="")
                        message = json.loads(self._bully_instance.receive_buffer.pop(0))
                        print(message)
                        if message["approved"]:
                        # move users from current to mainhall
                            members = r.getMembers()
                            for hall in serverstate.LOCAL_CHAT_ROOMS:

                                h_id = hall.getChatRoomId()

                                if h_id == mainHallName:

                                    for m in members:
                                        hall.addMember(m)
                            
                            # remove the room
                            serverstate.LOCAL_CHAT_ROOMS.remove(r)
                            return True,members,self._message_builder.deleteRoom(self._delete_room,"true")

                        else:
                            return False,[],self._message_builder.deleteRoom(self._delete_room,"false")
                        

                else:
                     # cannot delete the room
                    return False,[],self._message_builder.deleteRoom(self._delete_room,"false")
        
        # room does not exist cannot delete room
        return False,[],self._message_builder.deleteRoom(self._delete_room,"false")







                    

        
        