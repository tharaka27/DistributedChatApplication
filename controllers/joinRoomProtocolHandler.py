from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from flask import jsonify
from algorithms.fastbully import Bully 
import json
import time

class joinRoomProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "joinroom"
        self._roomid = json_data["roomid"]
        self._bully_instance = Bully._instance
        print( "Bully instance in new Identity" )
        print(self._bully_instance)
        
    def handle(self):
        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            print("[Error] Coordinator not alive")
            return jsonify({"error" : "Coordinator not alive"})

        
        local_roomIDs = serverstate.LOCAL_CHAT_ROOMS.keys()
        all_roomIDs = local_roomIDs + serverstate.REMOTE_CHAT_ROOMS

        # check whether requested room exists in any server
        if self._roomid in all_roomIDs:

            #check weather room exists in local server
            if self._roomid in local_roomIDs:
                print("room change broadcast")
                #broadcast roomchange message to all users in new room as well as old room

        else:
            # room does not exist
            # send roomchange with source and destination set to same
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
            if message["approved"] == "True" :
                serverstate.ALL_USERS.append(self._name)
                serverstate.LOCAL_USERS.append(self._name)
                return jsonify({ "type" : "newidentity" ,"approved": "True"})

            else:
                return jsonify({ "type" : "newidentity" ,"approved": "False"})
        