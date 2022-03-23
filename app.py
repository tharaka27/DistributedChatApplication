import socket               # Import socket module
import threading
import json
import signal
import sys
import time
from controllers.newIdentityProtocolHandler import newIdentityProtocolHandler
from models import serverstate
from utilities.fileReader import FileReader
from algorithms.bully import Bully
from controllers.JSONMessageBuilder import MessageBuilder 
import os

def connection_handler(connection,add):


    identity = "" # keeps identity of the connected client

    while True:

        try:
            req = connection.recv(1024)
            req = json.loads(req)

            operation = req['type']

            if operation == 'newidentity':

                print("[INFO] New Identity Request Received")

                # ----------------- dummy testing -----------------
                response = newIdentityProtocolHandler(req).handle()
                response = response + "\n"
                print(response)
                connection.send(response.encode('utf-8'))

                response2 = {"type" : "roomchange", "identity" : "tharaka", "former" : "", "roomid" : "MainHall-s1"}
                response2 = json.dumps(response2)+ "\n"

                connection.send(response2.encode("utf-8"))
                '''
                response = {"type":"newidentity","approved":"true"}
                response = json.dumps(response) + "\n"
        
                connection.send(response.encode("utf-8"))

                response2 = {"type" : "roomchange", "identity" : "vihan", "former" : "", "roomid" : "MainHall-s1"}
                response2 = json.dumps(response2)+ "\n"

                connection.send(response2.encode("utf-8"))
                '''

                
        except:
            print("Error occured in client ",identity,"!")
            connection.close()
            quit()
            continue

def Main():
    # Server intialization

    s = socket.socket()         # Create a socket object
    try:
        s.bind((serverstate.LOCAL_SERVER_CONFIGURATION.getAddress(), \
            int(os.environ.get('port'))))        # Bind to the port
    
    except:
        print("[INFO] Port is already Occupied\nShutting down the server")
        sys.exit(0)
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
    FILE_PATH = input("servers_conf :")
    
    f = FileReader()
    config_objects = f.populate(FILE_PATH)
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

    print("[INFO] Creating the mainhall in the server")
    mainHallName =  "MainHall-" + serverstate.LOCAL_SERVER_CONFIGURATION.getServerName()
    serverstate.LOCAL_CHAT_ROOMS[mainHallName] = []
    print(serverstate.LOCAL_CHAT_ROOMS)

    print("[INFO] Remote server configurations")
    print( serverstate.REMOTE_SERVER_CONFIGURATIONS)

    bully  = Bully()
    bully.run()

    msg = MessageBuilder.getInstance()
    Main()