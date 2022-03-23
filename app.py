import socket               # Import socket module
import threading
import json
import signal
import sys
import time


def connection_handler(connection,add):


    identity = "" # keeps identity of the connected client

    while True:

        try:
            req = connection.recv(1024)
            req = json.loads(req)

            operation = req['type']

            if operation == 'newidentity':

                print("new identity recived")

                # handle new identity

                # ----------------- dummy testing -----------------
                response = {"type":"newidentity","approved":"true"}
                response = json.dumps(response) + "\n"
        
                connection.send(response.encode("utf-8"))

                response2 = {"type" : "roomchange", "identity" : "vihan", "former" : "", "roomid" : "MainHall-s1"}
                response2 = json.dumps(response2)+ "\n"

                connection.send(response2.encode("utf-8"))

                
        except:
            print("Error occured in client ",identity,"!")
            connection.close()
            continue
    

# Server intialization

s = socket.socket()         # Create a socket object
s.bind(('127.0.0.1', 12345))        # Bind to the port
s.listen(20)                 # Now wait for client connection.

print ('Server started!')
print ('Waiting for clients...')

while True:
    print("next connection")
    connection, address = s.accept()
    # create a connection handler for the connected client
    threading.Thread(target=connection_handler,args=(connection,address)).start()