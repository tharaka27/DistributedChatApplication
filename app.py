import socket               # Import socket module
import threading
import json
import signal
import sys
import time
from controllers.newIdentityProtocolHandler import newIdentityProtocolHandler
from controllers.createRoomProtocolHandler import createRoomProtocolHandler
from controllers.whoProtocolHandler import whoProtocolHandler
from controllers.messageProtocolHandler import messageProtocolHandler
from models import serverstate
from utilities.fileReader import FileReader
from algorithms.bully import Bully
from controllers.JSONMessageBuilder import MessageBuilder 
from models.localroominfo import LocalRoomInfo
import os

global mainHallName

Messages = {}

def connection_handler(connection,add):

    connection.settimeout(3)

    identity = "" # keeps identity of the connected client
    global mainHallName
    chatroomid = mainHallName
    local_chat_pointer = 0
    ifFirstTime = True

    while True:
        
        
        if not(ifFirstTime) and local_chat_pointer < len(Messages[chatroomid]):
            buffer = {"type" : "message", "identity" : Messages[chatroomid][local_chat_pointer][0], \
                "content" : Messages[chatroomid][local_chat_pointer][1]}
            local_chat_pointer = local_chat_pointer + 1
            buffer_json = json.dumps(buffer) + "\n"
            connection.send(buffer_json.encode('utf-8'))
        
        
        try:
            req = connection.recv(1024)
            req = json.loads(req)

            operation = req['type']

            if operation == 'newidentity':

                ifFirstTime = False

                print("[INFO] New Identity Request Received")
                success,identity, response = newIdentityProtocolHandler(req).handle()

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))
                
                if success:
                    response2 = {"type" : "roomchange", "identity" : identity, \
                        "former" : "", "roomid" : mainHallName}
                    response2 = json.dumps(response2)+ "\n"

                    connection.send(response2.encode("utf-8"))
                
                for room in serverstate.ALL_CHAT_ROOMS:
                    if room.getChatRoomId() == chatroomid:
                        room.addMember(identity)
                
                for room in serverstate.LOCAL_CHAT_ROOMS:
                    if room.getChatRoomId() == chatroomid:
                        room.addMember(identity)
            
            
            elif operation == 'createroom':
                print("[INFO] Create Room Request Received")

                success, chatroomid, response = createRoomProtocolHandler(identity,req).handle()
                print("Hello world")
                print(response)

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))

                if success:
                    response2 = {"type" : "roomchange", "identity" : identity, "former" : "", "roomid" : chatroomid}
                    response2 = json.dumps(response2)+ "\n"

                    connection.send(response2.encode("utf-8"))
                else:
                    # if unsuccessful set the chatroomid back to mainhall
                    chatroomid = mainHallName
            
            elif operation == "who":
                print("[INFO] WHO Request Received")
                
                response = messageProtocolHandler(chatroomid, )
                
                print(response)

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))
            
            elif operation == "message":
                print("[INFO] Message Request Received")
                
                #response = whoProtocolHandler(chatroomid, req).handle()
                try:
                    Messages[chatroomid].append((identity,req['content']))
                except Exception as e:
                    print("[Error] {}".format(e))
                    Messages[chatroomid] = []
                
                print(Messages[chatroomid])
                #connection.send(response.encode('utf-8'))

            
            
                
        except:
            print("Timeout occured in client ",identity,"!")
            #connection.close()
            #quit()

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
    global mainHallName
    mainHallName =  "MainHall-" + serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
    chat_room_instance = LocalRoomInfo()
    chat_room_instance.setChatRoomID(mainHallName)
    chat_room_instance.setOwner("")
    chat_room_instance.setCoordinator(serverstate.LOCAL_SERVER_CONFIGURATION.getServerName())
    
    serverstate.LOCAL_CHAT_ROOMS.append(chat_room_instance)
    print(serverstate.LOCAL_CHAT_ROOMS)

    # setup message dictionary
    Messages[mainHallName] = []

    print("[INFO] Remote server configurations")
    print( serverstate.REMOTE_SERVER_CONFIGURATIONS)

    bully  = Bully()
    bully.run()

    msg = MessageBuilder.getInstance()
    Main()