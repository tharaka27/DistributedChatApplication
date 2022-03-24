from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.bully import Bully 
import json
import time

class listProtocolHandler:
    def __init__(self):
        self._protocol = "list"
        self._bully_instance = Bully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling list request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            return self._message_builder.coordinatorNotAlive(self._protocol)

        try:
            rooms = []
            for room in serverstate.ALL_CHAT_ROOMS:
                rooms.append(room.getChatRoomId())
            return self._message_builder.listProtocol(rooms)

        except Exception as e:
            print(e)
        
        