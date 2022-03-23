import zmq
import time
import parse
import sys
import threading
from models import serverstate
import json
import random
from controllers.JSONMessageBuilder import MessageBuilder
from models.localroominfo import LocalRoomInfo

class Bully:

    _instance = None

    def __init__(self):
        if Bully._instance != None:
            raise Exception("This is a singleton class") 
        else:
            Bully._instance = self
        self.max_id = serverstate.LOCAL_SERVER_CONFIGURATION.getId()
        self.address =  serverstate.LOCAL_SERVER_CONFIGURATION.getAddress()
        self.port = serverstate.LOCAL_SERVER_CONFIGURATION.getCoordinationPort()
        self.heart_port = serverstate.LOCAL_SERVER_CONFIGURATION.getHeartPort()
        self.processes = serverstate.REMOTE_SERVER_CONFIGURATIONS
        self.id = serverstate.LOCAL_SERVER_CONFIGURATION.getId()
        self.coor_id = -1
        self.send_buffer = []
        self.receive_buffer = []
        self.task_list = []
        self.msg_builder = MessageBuilder.getInstance()
        for p in self.processes:
            print(p)
            if self.max_id < p.getId():
                self.max_id = p.getId()
        print("[Configuration] ip:{} coor:{} heart:{}".format(self.address, self.port, self.heart_port))
    
    @staticmethod
    def getInstance():
        if Bully._instance == None:
            Bully()
        return Bully()._instance

    def connect_to_higher_ids(self):
        for p in self.processes:
            if int(p.getId()) > int(self.id):
                self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
        # so that last process does not block on send...
        #self.socket2.connect('tcp://{}:{}'.format(p['ip'], 55555))

    def connect_all(self):
        for p in self.processes:
            if p.getId() != self.id:
                self.heart_socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getHeartPort()))

    def connect_to_coordinator(self):
        for p in self.processes:
            # Connect to coordinator
            if p.getId() == int(self.coor_id) and not(p.getId() == int(self.id)):
                print("[INFO] connected to tcp://{}:{}".format(p.getAddress(), p.getCoordinationPort()) )
                self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
        

    def establish_connection(self, TIMEOUT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
        self.socket2 = self.context.socket(zmq.REQ)
        self.socket2.setsockopt(zmq.RCVTIMEO, TIMEOUT) #TIMEOUT
        self.socket_coor = self.context.socket(zmq.REQ)
        self.socket_coor.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        self.connect_to_higher_ids()
        self.heart_context = zmq.Context()
        self.heart_socket = self.heart_context.socket(zmq.PUB)
        self.heart_socket.bind('tcp://{}:{}'.format(self.address, self.heart_port))
        self.heart_socket2 = self.heart_context.socket(zmq.SUB)
        heart_timeout = 500*random.randint(4,10)
        self.heart_socket2.setsockopt(zmq.RCVTIMEO, heart_timeout)
        self.connect_all()
        self.heart_socket2.subscribe("")

    def update_coor(self, address, port, id):
        self.coor_ip = address
        self.coor_port = port
        self.coor_id = id 

    def heart_beats(self, proc=None):

        if proc == 'coor':
            while int(self.coor_id) == int(self.id):
                task_instance = ""
                if not(len(self.task_list)== 0):
                    task_instance = self.task_list.pop(0)
                message = {'type' : 'alive', 'address': self.address, \
                    'port': self.heart_port, 'id': self.id, 'task' : task_instance }
                self.heart_socket.send_string(json.dumps(message))
                
                serverstate.AMICOORDINATOR = True
                serverstate.ISCOORDINATORALIVE = True
                time.sleep(1)

        else:
            while True:
                try:
                    coor_heart_beat = self.heart_socket2.recv_string()
                    request = json.loads(coor_heart_beat)

                    if request['type']== 'alive' and request['id'] > self.id:
                        print("[HEARTBEAT]  {}".format(coor_heart_beat))
                        self.update_coor(request['address'], request['port'], int(request['id']))
                        serverstate.ISCOORDINATORALIVE = True
                        serverstate.AMICOORDINATOR = False
                        
                        # check whether their is a task
                        if not(request['task'] == ''):
                            # handle create_identity task
                            if request['task']['type'] == 'create_identity':
                                if not(request['task']["identity"] in serverstate.ALL_USERS) :
                                    serverstate.ALL_USERS.append(request['task']["identity"])
                                    print("[INFO] Added new user {} to the ALL_USERS ".format(\
                                        request['task']["identity"]))
                            elif request['task']['type'] == 'create_chat_room':
                                isRoomExist = False
                                for room in serverstate.ALL_CHAT_ROOMS:
                                    if room.getId == self._roomid:
                                        isRoomExist = True
                                
                                if not(isRoomExist):
                                    chat_room_instance = LocalRoomInfo()
                                    chat_room_instance.setChatRoomID(request['task']['roomid'])
                                    chat_room_instance.setOwner(request['task']['identity'])
                                    chat_room_instance.setCoordinator(request['task']['server'])
                                    chat_room_instance.addMember(request['task']['identity'])
                                    serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)
                                    print("[INFO] Added new chatroom {} to the ALL_CHAT_ROOMS ".format(\
                                        request['task']["roomid"]))

                except:

                    if self.coor_id != self.id:
                        print("[INFO] Coordinator is dead, get ready for election \n")
                        self.coor_id = -1
                        serverstate.ISCOORDINATORALIVE = False
                        serverstate.AMICOORDINATOR = False
                        

    def run_server(self):
        
        while True:
            try:
                request = self.socket.recv_string()
                print("[Info] A new packat received.")
                if request.startswith('election'):
                    self.socket.send_string('alive')
                    continue

                req = json.loads(request)
                if req['type'] == 'create_identity' and self.id == self.coor_id:
                    print("[INFO] Received create_identity task")
                    if req["identity"] in serverstate.ALL_USERS :
                        print("[Request] Create a new identity ", req["identity"], " unsuccessful")
                        self.socket.send_string(self.msg_builder.createNewIdentity(False))
                    else:
                        print("[Request] Create a new identity ", req["identity"], " successful")
                        
                        # add user to the all user catalogue
                        serverstate.ALL_USERS.append(req["identity"])

                        # send message to all servers through pub-sub scheme
                        self.task_list.append({"type" : "create_identity", "identity":req["identity"]})
                        
                        # send success message to the server
                        self.socket.send_string(self.msg_builder.createNewIdentity(True)) 

                elif req['type'] == 'create_chat_room' and self.id == self.coor_id:
                    isRoomExist = False
                    for room in serverstate.ALL_CHAT_ROOMS:
                        if room.getId == req['roomid']:
                            isRoomExist = True
                                
                    if not(isRoomExist):
                        # success
                        chat_room_instance = LocalRoomInfo()
                        chat_room_instance.setChatRoomID(req['roomid'])
                        chat_room_instance.setOwner(req['identity'])
                        chat_room_instance.setCoordinator(req['server'])
                        chat_room_instance.addMember(req['identity'])
                        serverstate.ALL_CHAT_ROOMS.append(chat_room_instance)
                        print("[INFO] Added new chatroom {} to the ALL_CHAT_ROOMS ".format(\
                                    req["roomid"]))
                        self.socket.send_string(self.msg_builder.createNewChatRoom(True)) 
                    else:
                        self.socket.send_string(self.msg_builder.createNewChatRoom(False)) 


                else:
                    self.socket.send_string(self.msg_builder.errorServer())

            except json.decoder.JSONDecodeError as e:
                print("[Warning] Trying to decode election message")
            
            except zmq.ZMQError as e:
                
                self.socket.close()
                self.socket = self.context.socket(zmq.REP)
                self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
                
    
    def declare_am_coordinator(self):
        print('[INFO] I am the coordinator')
        serverstate.AMICOORDINATOR = True
        serverstate.ISCOORDINATORALIVE = True
        self.update_coor(self.address, self.heart_port, self.id)
        heart_beats_thread = threading.Thread(target=self.heart_beats, args=['coor'])
        heart_beats_thread.start()

    def run_msg_sender(self):
        while True:
            if self.coor_id == -1 or (self.id == self.coor_id):
                continue
            else:
                if not(len(self.send_buffer) == 0):
                    message = self.send_buffer.pop(0)
                
                    # get coordinator address and port
                    address, port = "", ""
                    for p in self.processes:
                        if int(p.getId()) == self.coor_id:
                            address = p.getAddress()
                            port = p.getCoordinationPort()
                            break
                    try:
                        print("[INFO] Trying to send message to the coordinator ({},{})".format(\
                            address,port), message)
                        self.socket_coor.connect('tcp://{}:{}'.format(address, port))
                        self.socket_coor.send_string(json.dumps(message))
                        req = self.socket_coor.recv_string()
                        self.receive_buffer.append(req)
                        print("[INFO] Receive complete")
                        
                    except zmq.ZMQError as e:
                        # try restarting the socket connection
                        self.socket_coor.close(0)
                        self.socket_coor = self.context.socket(zmq.REQ)
                        self.socket_coor.setsockopt(zmq.RCVTIMEO, 2000)
                        print("[Error] {}".format(e))
                        self.send_buffer.append(message)
                
            time.sleep(1)


    def run_client(self):
        while True:
            if self.coor_id == -1:
                print("[INFO] Starting election procedure")
                
                try:
                    if self.id == self.max_id:
                        self.declare_am_coordinator()
                    else: # goes if self.id < self.maxID
                        self.socket2.send_string('election')
                        req = self.socket2.recv_string()
                        
                except :
                    print("[Error] Error occured while trying to start election")
                    self.declare_am_coordinator()

            time.sleep(1)

    def run(self):
        self.establish_connection(5000)

        heart_beats_thread = threading.Thread(target=self.heart_beats, args=[])
        heart_beats_thread.start()

        serv_thread = threading.Thread(target=self.run_server, args=[])
        serv_thread.start()

        client_thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()

        msg_sender_thread = threading.Thread(target=self.run_msg_sender, args=[])
        msg_sender_thread.start()