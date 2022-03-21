from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from flask import jsonify
from algorithms.fastbully import Bully 
import json
import time

class newIdentityProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "newidentity"
        self._name = json_data["identity"]
        self._bully_instance = Bully._instance
        print( "Bully instance in new Identity" )
        print(self._bully_instance)
        
    def handle(self):
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            print("[Error] Coordinator not alive")
            return jsonify({"error" : "Coordinator not alive"})

        # check whether I am coordinator
        if serverstate.AMICOORDINATOR:

            # the user exists
            if self._name in serverstate.ALL_USERS :
                return jsonify({ "type" : "newidentity" ,"approved": "False"})

            else:
                serverstate.ALL_USERS.append(self._name)
                return jsonify({ "type" : "newidentity" ,"approved": "True"})

        else:
            # forward the message to the coordinator
            print("[INFO] Forwardig the create_identity request to coordinator")
            message = { "type" : "create_identity" , "identity" : self._name}
            #self._bully_instance.socket2.send_string(json.dumps(message))
            #request =  self._bully_instance.socket2.recv_string()
            #req = json.loads(request)
            #print("[INFO] Received the ", request)

            self._bully_instance.send_buffer.append(message)

            while(len(self._bully_instance.receive_buffer) == 0):
                time.sleep(1)
            
            print("[Received]", end="")
            message = json.loads(self._bully_instance.receive_buffer.pop(0))
            print(message)
            if message["approved"] :
                serverstate.ALL_USERS.append(self._name)
                serverstate.LOCAL_USERS.append(self._name)
                return jsonify({ "type" : "newidentity" ,"approved": "True"})

            else:
                return jsonify({ "type" : "newidentity" ,"approved": "False"})
        