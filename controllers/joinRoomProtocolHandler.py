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
        self._message_builder = MessageBuilder._instance
        print( "Bully instance in new Identity" )
        print(self._bully_instance)
        
    def handle(self,current_room,identity):
        print("[INFO] Handling joinroom request started.")

        # check whether coordinator is alive
        if not(serverstate.ISCOORDINATORALIVE):
            print("[Error] Coordinator not alive")
            return jsonify({"error" : "Coordinator not alive"})

        # checking weather client is the admin of currentroom
        for l_r in serverstate.LOCAL_CHAT_ROOMS:
            
            if current_room == l_r.getChatRoomId():

                if l_r.getOwner() == identity:

                    #cannot join room because he/she owns the current room
                    return [],self._message_builder.roomChange(identity,current_room,current_room)


        # checking weather the room is in local server
        for l_r in serverstate.LOCAL_CHAT_ROOMS:
            
            if self._roomid == l_r.getChatRoomId():

                if l_r.getOwner() == identity:

                    #cannot join room because he/she owns the current room
                    return [],self._message_builder.roomChange(identity,current_room,current_room)
        
        remote_roomIDs = []
        for room in serverstate.REMOTE_CHAT_ROOMS:
            remote_roomIDs.append(room.getChatRoomId())

        all_roomIDs = local_roomIDs + remote_roomIDs

        # check whether requested room exists in any server
        if self._roomid in all_roomIDs:

                # check weather she is the admin in current room
                current_room_info = serverstate.LOCAL_CHAT_ROOMS[current_room]
                admin = current_room_info['admin']

                # if yes
                if admin == identity:
                    #cannot join room because he/she owns the current room
                    return [],self._message_builder.roomChange(identity,current_room,current_room)
                
                # if no
                else:
                    #check weather room exists in local server
                    if self._roomid in local_roomIDs:

                            #broadcast roomchange message to all users in new room as well as old room
                            brodcast_id_list = serverstate.LOCAL_CHAT_ROOMS[current_room]['people'] + serverstate.LOCAL_CHAT_ROOMS[self._roomid]['people']
                            msg = self._message_builder.roomChange(identity,current_room,self._roomid)
                            return brodcast_id_list, msg

                    else:
                        # room is in a different server
                        server_id_room = serverstate.REMOTE_CHAT_ROOMS[self._roomid]


        else:
            # room does not exist in any server
 
        