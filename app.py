import socket               # Import socket module
import threading
import json
import signal
import sys
import time
from controllers.newIdentityProtocolHandler import newIdentityProtocolHandler
from controllers.createRoomProtocolHandler import createRoomProtocolHandler
from controllers.whoProtocolHandler import whoProtocolHandler
from controllers.joinRoomProtocolHandler import joinRoomProtocolHandler
from models import serverstate
from utilities.fileReader import FileReader
from algorithms.bully import Bully
from controllers.JSONMessageBuilder import MessageBuilder 
from models.localroominfo import LocalRoomInfo
import os

global mainHallName
global broadcast_pool
broadcast_pool = {}

def connection_handler(connection,add):


    identity = "" # keeps identity of the connected client
    global mainHallName
    chatroomid = mainHallName
    bd_index = 0

    connection.settimeout(3)

    while True:
        
        try:
            req = connection.recv(1024)
            req = json.loads(req)

            operation = req['type']

            if operation == 'newidentity':

                print("[INFO] New Identity Request Received")
                success,identity, response = newIdentityProtocolHandler(req).handle()

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))
                
                if success:
                    response2 = {"type" : "roomchange", "identity" : identity, \
                        "former" : "", "roomid" : mainHallName}
                    response2 = json.dumps(response2)+ "\n"

                    bd_index = len(broadcast_pool[chatroomid])

                    connection.send(response2.encode("utf-8"))
                
                for room in serverstate.ALL_CHAT_ROOMS:
                    if room.getChatRoomId() == chatroomid:
                        room.addMember(identity)
                
                for room in serverstate.LOCAL_CHAT_ROOMS:
                    if room.getChatRoomId() == chatroomid:
                        room.addMember(identity)
            
            
            elif operation == 'createroom':
                print("[INFO] Create Room Request Received")

                newroomid, response = createRoomProtocolHandler(identity,req).handle()
                print("Hello world")
                print(response)

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))

                broadcast_pool[chatroomid].append(response)
                chatroomid = newroomid
                broadcast_pool[chatroomid] = []


                response2 = {"type" : "roomchange", "identity" : identity, "former" : "", "roomid" : chatroomid}
                response2 = json.dumps(response2)+ "\n"

                connection.send(response2.encode("utf-8"))

            elif operation == 'joinroom':

                print("[INFO] Join Room Request Received")

                broadcast,response = joinRoomProtocolHandler(identity,chatroomid,req).handle()

                response = response + "\n"

                if broadcast == "b":
                    broadcast_pool[chatroomid].append(response)
                    broadcast_pool[req['roomid']].append(response)
                    chatroomid = req['roomid']

                elif broadcast == "o":
                    broadcast_pool[chatroomid].append(response)
                    chatroomid = req['roomid']
                    
                connection.send(response.encode("utf-8"))
            
            elif operation == "who":
                print("[INFO] WHO Request Received")
                
                response = whoProtocolHandler(chatroomid).handle()
                
                print(response)

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))

            
        except socket.timeout:

            if bd_index < (len(broadcast_pool[chatroomid])):
                
                print(bd_index,len(broadcast_pool[chatroomid]))
                while(bd_index < len(broadcast_pool[chatroomid])):
                    msg = broadcast_pool[chatroomid][bd_index]
                    connection.send(msg.encode('utf-8'))
                    bd_index = bd_index +1
            
            continue


        except:
            print("Error occured in client ",identity,"!")
            connection.close()
            quit()

def Main():
    # Server intialization

    s = socket.socket()         # Create a socket object
    try:
        s.bind((serverstate.LOCAL_SERVER_CONFIGURATION.getAddress(), \
            int(os.environ.get('port'))))        # Bind to the port
    
    except:
        print("[INFO] Port is already Occupied\nShutting down the server")
        quit()
    s.listen(20)                 # Now wait for client connection.

    print ('Server started!')
    print ('Waiting for clients...')

    while True:
        print("next connection")
        connection, address = s.accept()
        # create a connection handler for the connected client
        threading.Thread(target=connection_handler,args=(connection,address)).start()


if __name__ == "__main__":
    
    LOCAL_SERVER_NAME = input("serverid :")
    #FILE_PATH = input("servers_conf :")
    
    f = FileReader()
    #config_objects = f.populate(FILE_PATH)
    config_objects = f.populate('configuration.txt')
    for i in config_objects:

        print("Setting ->" + i.getServerName() + i.getAddress() + ":" + str(i.getHeartPort()))
        if i.getServerName() == LOCAL_SERVER_NAME:
            serverstate.LOCAL_SERVER_CONFIGURATION = i
            #LOCAL_SERVER_CONFIGURATION = i
        else:
            serverstate.REMOTE_SERVER_CONFIGURATIONS.append(i)
            #REMOTE_SERVER_CONFIGURATIONS.append(i)


    print("[INFO] Initializing server with.....")   
    print("[INFO] Local server configuration")
    print( serverstate.LOCAL_SERVER_CONFIGURATION )

    # add main hall to the local chat room set
    print("[INFO] Creating the mainhall in the server")
    #global mainHallName
    mainHallName =  "MainHall-" + serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
    chat_room_instance = LocalRoomInfo()
    chat_room_instance.setChatRoomID(mainHallName)
    chat_room_instance.setOwner("")
    chat_room_instance.setCoordinator(serverstate.LOCAL_SERVER_CONFIGURATION.getServerName())

    serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)
    broadcast_pool[mainHallName] = []

    print(serverstate.LOCAL_CHAT_ROOMS)

    print("[INFO] Remote server configurations")
    print( serverstate.REMOTE_SERVER_CONFIGURATIONS)

    bully  = Bully()
    bully.run()

    msg = MessageBuilder.getInstance()
    Main()