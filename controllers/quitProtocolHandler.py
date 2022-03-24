from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.bully import Bully 
from models.localroominfo import LocalRoomInfo
import json
import time

class quitProtocolHandler:
    def __init__(self,identity):
        self._protocol = "quit"
        self._identity = identity
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):

        print("[INFO] Handling quit request started.")
        # check whether coordinator is alive

        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        #checks in all rooms weather the room exists
        for u in serverstate.LOCAL_USERS:

            if u == self._identity:

                if serverstate.AMICOORDINATOR:
                    print("[INFO] Handling quit inside AMICOORDINATOR.")
                    
                    # remove user
                    serverstate.ALL_USERS.remove(u)
                    serverstate.LOCAL_USERS.remove(u)

                    try:
                        self._bully_instance.task_list.append({"type" : "quit","identity": self._identity})
                        return True
                    except :
                        print("[Error] Error occured while distributing the delete room")

                    print("[INFO] FINISHED")
                
                else:

                    # forward the message to the coordinator
                    print("[INFO] Forwarding the deleteroom request to coordinator")

                    message = {"type" : "quit","identity": self._identity}
                    
                    self._bully_instance.send_buffer.append(message)

                    while(len(self._bully_instance.receive_buffer) == 0):
                        time.sleep(1)
                    
                    print("[Received]", end="")
                    message = json.loads(self._bully_instance.receive_buffer.pop(0))
                    print(message)
                    if message["approved"]:
                        # remove user
                        serverstate.ALL_USERS.remove(u)
                        serverstate.LOCAL_USERS.remove(u)

                        return True

                    else:
                        return False
                    
        
        # room does not exist in current server
        return False







                    

        
        