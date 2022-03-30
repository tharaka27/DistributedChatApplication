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
from controllers.moveJoinProtocolHandler import moveJoinProtocolHandler
from controllers.messageProtocolHandler import messageProtocolHandler
from controllers.deleteRoomProtocolHandler import deleteRoomProtocolHandler
from controllers.quitProtocolHandler import quitProtocolHandler
from controllers.listProtocolHandler import listProtocolHandler
from models import serverstate
from utilities.fileReader import FileReader
from algorithms.bully import Bully
from controllers.JSONMessageBuilder import MessageBuilder 
from models.localroominfo import LocalRoomInfo
import os

global mainHallName
global broadcast_pool

broadcast_pool = {}

Messages = {}

def connection_handler(connection,add):

    connection.settimeout(3)

    identity = "" # keeps identity of the connected client
    global mainHallName
    chatroomid = mainHallName
    bd_index = 0
    local_chat_pointer = 0
    ifFirstTime = True

    connection.settimeout(3)

    while True:

        if not(ifFirstTime) and local_chat_pointer < len(Messages[chatroomid]):
            buffer = {"type" : "message", "identity" : Messages[chatroomid][local_chat_pointer][0], \
                "content" : Messages[chatroomid][local_chat_pointer][1]}
            buffer_json = json.dumps(buffer) + "\n"
            local_chat_pointer = local_chat_pointer + 1
            if not(identity == Messages[chatroomid][local_chat_pointer-1][0]):
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

                old_room = chatroomid

                success, chatroomid, response = createRoomProtocolHandler(identity,req).handle()
                print("Hello world")
                print(response)

                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))

                if success:
                    response2 = {"type" : "roomchange", "identity" : identity, "former" : "", "roomid" : chatroomid}
                    response2 = json.dumps(response2)+ "\n"

                    broadcast_pool[old_room].append(response2)
                    broadcast_pool[chatroomid] = []
                    Messages[chatroomid] = []

                    connection.send(response2.encode("utf-8"))

                    Messages[chatroomid] = []
                else:
                    # if unsuccessful set the chatroomid back to mainhall
                    chatroomid = mainHallName


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

            elif operation == "movejoin":

                print("[INFO] Move join Request Received")

                identity = req['identity'] 
                ifFirstTime = False
                broadcast,response = moveJoinProtocolHandler(identity,req['former'],req).handle()

                response = response + "\n"

                if (broadcast):
                    response2 = {"type" : "roomchange", "identity" : identity, "former" : req['former'], "roomid" : req['roomid']}
                    response2 = json.dumps(response2)+ "\n"
                    broadcast_pool[req['roomid']].append(response2)
                    Messages[req['roomid']] = []
                    bd_index = len(broadcast_pool[req['roomid']])
                    chatroomid = req['roomid']
                    connection.send(response.encode('utf-8'))
                    connection.send(response2.encode('utf-8'))
                else:
                    broadcast_pool[mainHallName].append(response)
                    bd_index = len(broadcast_pool[mainHallName])
                    chatroomid = mainHallName
                    connection.send(response.encode('utf-8'))

            elif operation == "deleteroom":

                print("[INFO] Delete Room Request Received")
                broadcast,members,response = deleteRoomProtocolHandler(identity,req).handle()

                if broadcast:
                    for m in members:
                        msg = {"type" : "roomchange", "identity" : m, "former" : req['roomid'], "roomid" : mainHallName}
                        msg = json.dumps(msg)+ "\n"
                        broadcast_pool[req["roomid"]].append(msg)
                
                response =response + "\n"
                connection.send(response.encode('utf-8'))
            
            elif operation == "list":

                print("[INFO] List Room Request Received")
                response = listProtocolHandler().handle()

                response =response + "\n"
                connection.send(response.encode('utf-8'))

            elif operation == "quit": 

                print("[INFO] Quit Request Received")
                state = quitProtocolHandler(identity).handle()

                if state:

                    #find rooms owned by user
                    for r in serverstate.LOCAL_CHAT_ROOMS:
                        r_owner = r.getOwner()

                        if r_owner == identity:
                            #owns a room
                            room_id = r.getChatRoomId()
                            # delete room handler
                            data = {"roomid":room_id}
                            broadcast,members,response = deleteRoomProtocolHandler(identity,data).handle()

                            if broadcast:
                                for m in members:
                                    if m == identity:
                                        continue
                                    else:
                                        msg = {"type" : "roomchange", "identity" : m, "former" : room_id, "roomid" : mainHallName}
                                        msg = json.dumps(msg)+ "\n"
                                        broadcast_pool[room_id].append(msg)
                            break
                    
                    
                    response = {"type" : "roomchange", "identity" : identity, "former" : chatroomid, "roomid" : ""}
                    response = json.dumps(response)+ "\n"
                    connection.send(response.encode('utf-8'))
                    connection.close()
                    quit()
                else:
                    print("cannot quit")
                    

        except socket.timeout:

            time.sleep(1)

            if bd_index < (len(broadcast_pool[chatroomid])):
            
                while(bd_index < len(broadcast_pool[chatroomid])):
                    msg = broadcast_pool[chatroomid][bd_index]

                    data = json.loads(msg)
                    if data["type"] == "roomchange" and data["identity"] == identity:
                        chatroomid = data["roomid"] 
                    
                    connection.send(msg.encode('utf-8'))
                    bd_index = bd_index +1
            
            continue


        except:
            # think client send a quit message
            print("[INFO] Quit Request Received")
            state = quitProtocolHandler(identity).handle()

            if state:

                #find rooms owned by user
                for r in serverstate.LOCAL_CHAT_ROOMS:
                    r_owner = r.getOwner()

                    if r_owner == identity:
                        #owns a room
                        room_id = r.getChatRoomId()
                        # delete room handler
                        data = {"roomid":room_id}
                        broadcast,members,response = deleteRoomProtocolHandler(identity,data).handle()

                        if broadcast:
                            for m in members:
                                if m == identity:
                                    continue
                                else:
                                    msg = {"type" : "roomchange", "identity" : m, "former" : room_id, "roomid" : mainHallName}
                                    msg = json.dumps(msg)+ "\n"
                                    broadcast_pool[room_id].append(msg)
                        break
                
                
                response = {"type" : "roomchange", "identity" : identity, "former" : chatroomid, "roomid" : ""}
                response = json.dumps(response)+ "\n"
                connection.send(response.encode('utf-8'))
                connection.close()
                quit()
            else:
                print("cannot quit")


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


    # TODO create correct logic
    serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)

    broadcast_pool[mainHallName] = []

    print(serverstate.LOCAL_CHAT_ROOMS)

    # setup message dictionary
    Messages[mainHallName] = []

    print("[INFO] Remote server configurations")
    print( serverstate.REMOTE_SERVER_CONFIGURATIONS)

    bully  = Bully()
    bully.run()

    msg = MessageBuilder.getInstance()
    Main()