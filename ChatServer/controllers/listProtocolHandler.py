from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
from algorithms.bully import Bully
import json
import time

class listProtocolHandler:
    def __init__(self):
        self._protocol = "list"
        self._bully_instance = FastBully._instance
        #self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling List request started.")

        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        system_rooms = []

        if serverstate.AMICOORDINATOR:
            print("[INFO] Handling delete inside AMICOORDINATOR.")
            system_rooms = self._bully_instance.get_rooms()
            return self._message_builder.listProtocol(system_rooms)
        
        else:

            # forward the message to the coordinator
            print("[INFO] Forwarding the deleteroom request to coordinator")
            request = {"type":"get_list"}
            self._bully_instance.send_buffer.append(request)

            while(len(self._bully_instance.receive_buffer) == 0):
                time.sleep(1)
                        
            print("[Received]", end="")
            message = json.loads(self._bully_instance.receive_buffer.pop(0))
            print(message)
            if message["type"] == "room_list":

                system_rooms = message["rooms"]

            return self._message_builder.listProtocol(system_rooms)

        
