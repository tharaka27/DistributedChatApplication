from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from flask import jsonify
from algorithms.bully import Bully 
import json
import time

class newIdentityProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "newidentity"
        self._name = json_data["identity"]
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        # check whether I am coordinator
        if serverstate.AMICOORDINATOR:

            # the user exists
            if self._name in serverstate.ALL_USERS :
                return self._message_builder.newIdentity("False")

            else:
                serverstate.ALL_USERS.append(self._name)
                serverstate.LOCAL_USERS.append(self._name)
                return self._message_builder.newIdentity("True") 

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
                serverstate.ALL_USERS.append(self._name)
                serverstate.LOCAL_USERS.append(self._name)
                return self._message_builder.newIdentity("True") 
            else:
                return self._message_builder.newIdentity("False") 