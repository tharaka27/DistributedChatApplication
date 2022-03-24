from models import serverstate
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.bully import Bully 
import json
import time

class messageProtocolHandler:
    def __init__(self, roomid, json_data):
        self._protocol = "message"
        self._roomId = roomid
        self._content = json_data["content"]
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling who request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        

        

        