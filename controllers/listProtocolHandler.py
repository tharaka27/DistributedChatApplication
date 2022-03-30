from models import serverstate 
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder
from algorithms.fastbully import FastBully 
import json
import time

class listProtocolHandler:
    def __init__(self):
        self._protocol = "list"
        self._bully_instance = FastBully._instance
        self._message_builder = MessageBuilder._instance
        
    def handle(self):
        print("[INFO] Handling new identity request started.")

        system_rooms = []

        try:
            for room in serverstate.ALL_CHAT_ROOMS:

                room_id = room.getChatRoomId()
                system_rooms.append(room_id)

        except Exception as e:
            print(e)
        
        return self._message_builder.listProtocol(system_rooms)

        
