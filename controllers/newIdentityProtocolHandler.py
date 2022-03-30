from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
import json
import time

class newIdentityProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "newidentity"
        self._name = json_data["identity"]
        self._bully_instance = FastBully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling new identity request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return False, self._message_builder.coordinatorNotAlive(self._protocol)

        # imposing strict rules for the name
        name = str(self._name)
        
        if len(self._name) < 3 or len(self._name) > 16 or name[0].isdigit():
            return False,self._name, self._message_builder.newIdentity("False")

        # check whether I am coordinator
        if serverstate.AMICOORDINATOR:
            # the user exists
            if self._name in serverstate.ALL_USERS :
                print("[INFO] Handling new identity inside AMICOORDINATOR. User exists")
                return False,self._name, self._message_builder.newIdentity("False")

            else:
                print("[INFO] Handling new identity inside AMICOORDINATOR. User does not exist")

                try:
                    serverstate.ALL_USERS.append(self._name)
                    serverstate.LOCAL_USERS.append(self._name)
                except:
                    print("[Error] Unexpected error")
                # distribute it to the others
                try:
                    self._bully_instance.task_list.append({"type" : "create_identity", "identity":self._name})
                except :
                    print("[Error] Error occured while distributing the new identity")

                print("[INFO] FINISHED")
                return True,self._name,self._message_builder.newIdentity("True") 

        else:
            # forward the message to the coordinator
            print("[INFO] Forwarding the create_identity request to coordinator")
            message = { "type" : "create_identity" , "identity" : self._name}
            
            self._bully_instance.send_buffer.append(message)

            while(len(self._bully_instance.receive_buffer) == 0):
                time.sleep(1)
            
            print("[Received]", end="")
            message = json.loads(self._bully_instance.receive_buffer.pop(0))
            print(message)
            if message["approved"] == "True" :
                serverstate.LOCAL_USERS.append(self._name)
                return True,self._name,self._message_builder.newIdentity("True") 
            else:
                return False,self._name,self._message_builder.newIdentity("False") 