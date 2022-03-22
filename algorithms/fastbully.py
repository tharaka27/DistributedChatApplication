import zmq
import time
import parse
import sys
import threading
#from models.serverstate import LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS
from models import serverstate
import json
import random

class Bully:

    global Fast_enabled, coord_dead, election_started
    Fast_enabled = False
    coord_dead = False
    election_started = False
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
            # changed to connect all
            if p.getId() > int(self.id):
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

        global Fast_enabled,coord_dead,election_started

        if proc == 'coor':
            while int(self.coor_id) == int(self.id):
                message = {'type' : 'alive', 'address': self.address, \
                    'port': self.heart_port, 'id': self.id }
                self.heart_socket.send_string(json.dumps(message))
                
                if election_started:
                    election_started = False  
                
                serverstate.AMICOORDINATOR = True
                serverstate.ISCOORDINATORALIVE = True
                time.sleep(1)
        else:
            while True:
                try:
                    coor_heart_beat = self.heart_socket2.recv_string()
                    request = json.loads(coor_heart_beat)

                    if Fast_enabled :
                        #print("fast bully implementation...")
                        # check recived message

                         # if heart beat message
                        if(request['type'] == "alive"):
                            print("coordinator  {}".format(coor_heart_beat))
                            serverstate.ISCOORDINATORALIVE = True
                            self.update_coor(request['address'], request['port'], int(request['id'])) 
                            if election_started:
                                election_started = False   

                        # if coordinator dead message                        
                        elif (request['type'] == "dead"):
                            print("election is in process...")
                            election_started = True
                            serverstate.ISCOORDINATORALIVE = False

                        else:
                            print("Unkown message")
                        

                    else:
                        if request['id'] > self.id:
                            print("coordinator  {}".format(coor_heart_beat))
                            self.update_coor(request['address'], request['port'], int(request['id']))
                            serverstate.ISCOORDINATORALIVE = True
                            serverstate.AMICOORDINATOR = False
                
                except:
                    if Fast_enabled:

                        # other process has already started election
                        if (election_started):
                            print("election is in process...")
                            serverstate.ISCOORDINATORALIVE = False
                        
                        # I am the first to detect the failure
                        elif self.coor_id != self.id:
                            coord_dead = True
                            # Send dead message
                            message = {'type' : 'dead' }
                            self.heart_socket.send_string(json.dumps(message))
                            election_started = True
                            print("Coordinator is dead, get ready for election \n")
                            #self.start_election()
                            serverstate.ISCOORDINATORALIVE = False
                    

                    else:
                        if self.coor_id != self.id:
                            print("Coordinator is dead, get ready for election \n")
                            self.coor_id = -1
                            serverstate.ISCOORDINATORALIVE = False
                            serverstate.AMICOORDINATOR = False
                        
    
    '''
    def start_election(self):

        #self.declare_am_coordinator()

        res_ids = []
        coordinator_found = False
        # Get process with higher priority than self

        while (not coordinator_found):

            if self.id == self.max_id:
                print(" i am the highest")
                self.declare_am_coordinator()
                coordinator_found = True
                serverstate.ISCOORDINATORALIVE = True

            else: # goes if self.id < self.maxID

                message = {'type' : 'election'}
                self.socket2.send_string(json.dumps(message))

                while True:
                    try:
                        res = self.socket2.recv_string()
                        response = json.loads(res)
                        res_ids.append(response['id'])
                    except:
                        break

                if (len(res_ids)> 0):
                    
                    # Send nomination
                    while len(res_ids) > 0:

                        selected_cord = max(res_ids)
                        message = {'type' : 'nomination','id':selected_cord}
                        self.socket2.send_string(json.dumps(message))

                        try:
                            res2 = self.socket2.recv_string()
                            response2 = json.loads(res2)
                            if(response2['type'] == "coordinator" and response2['id'] == selected_cord):
                                print("New coordinator appointed !")
                                coordinator_found = True
                                break

                        except:
                            # Previous process did not respond
                            res_ids.remove(selected_cord)
                else:
                    self.declare_am_coordinator()
                    coordinator_found = True
        return True
    '''
    


    def run_server(self):

        global Fast_enabled

        if (Fast_enabled):

            while True:
                request = self.socket.recv_string()
                req = json.loads(request)
                if req['type']=='election':
                    #respond alive..with id
                    message = {'type' : 'alive','id': self.id}
                    self.socket.send_string(json.dumps(message))
                
                elif req['type']=='nomination':
                    if req['id'] == self.id:
                        message = {'type' : 'coordinator','id': self.id}
                        self.socket.send_string(json.dumps(message))
                        self.declare_am_coordinator()
                '''
                elif req['type'] == 'create_identity' and self.id == self.coor_id:
                    print("Received create_identity task")
                    if req["identity"] in serverstate.ALL_USERS :
                        print("[Request] Create a new identity", req["identity"], " .Unsuccessful")
                        message = { "type" : "create_identity_done" ,"approved": "False"}
                        self.socket.send_string(json.dumps(message))
                        
                    else:
                        message = { "type" : "create_identity_done" ,"approved": "True"}
                        print("[Request] Create a new identity", req["identity"], " .successful")
                        serverstate.ALL_USERS.append(req["identity"])
                        self.socket.send_string(json.dumps(message))
                '''

    
        else:
            while True:
                try:
                    request = self.socket.recv_string()
                    print("[Info] A new packat received.")
                    if request.startswith('election'):
                        print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjj respond alive")
                        self.socket.send_string('alive')
                        continue

                    req = json.loads(request)
                    if req['type'] == 'create_identity' and self.id == self.coor_id:
                        print("Received create_identity task")
                        if req["identity"] in serverstate.ALL_USERS :
                            print("[Request] Create a new identity", req["identity"], " .Unsuccessful")
                            message = { "type" : "create_identity_done" ,"approved": "False"}
                            self.socket.send_string(json.dumps(message))
                        else:
                            message = { "type" : "create_identity_done" ,"approved": "True"}
                            print("[Request] Create a new identity", req["identity"], " .successful")
                            serverstate.ALL_USERS.append(req["identity"])
                            self.socket.send_string(json.dumps(message)) 
                    else:
                        message = { "type" : "error message" }
                        self.socket.send_string(json.dumps(message))

                except json.decoder.JSONDecodeError as e:
                    print("[Warning] Trying to decode election message")
                
                except zmq.ZMQError as e:
                    
                    self.socket.close()
                    self.socket = self.context.socket(zmq.REP)
                    self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
                
    
    def declare_am_coordinator(self):
        print('I am the coordinator')
        serverstate.AMICOORDINATOR = True
        serverstate.ISCOORDINATORALIVE = True
        self.update_coor(self.address, self.heart_port, self.id)
        heart_beats_thread = threading.Thread(target=self.heart_beats, args=['coor'])
        heart_beats_thread.start()


    def run_client(self):

        global coord_dead

        if Fast_enabled:
            print("client running ..")

            while True:
                if coord_dead:
                   result = self.start_election() 
                   if result:
                       coord_dead = False

                '''
                # if not empty send message
                if not(len(self.send_buffer) == 0 or self.coor_id == -1):
                    message = self.send_buffer.pop(0)

                    try:
                        self.socket2.send_string(json.dumps(message))
                        print("send string")
                        #time.sleep(1)
                        request = self.socket2.recv_string()
                        self.receive_buffer.append(request)
                        print("receive complete")
                    except zmq.ZMQError as e:
                        if e.errno == zmq.EAGAIN:
                            self.send_buffer.append(message)
                        else:
                            print(e)
                '''

                time.sleep(1)

        else:
            while True:
                if self.coor_id == -1:
                    try:
                        if self.id == self.max_id:
                            self.declare_am_coordinator()
                        else: # goes if self.id < self.maxID
                            self.socket2.send_string('election')
                            req = self.socket2.recv_string()
                    except:
                        self.declare_am_coordinator()

                 # if not empty send message
                if not(len(self.send_buffer) == 0 or self.coor_id == -1):
                    message = self.send_buffer.pop(0)
                    print("[INFO] Trying to send message", message)
                    self.connect_to_coordinator()
                    self.socket2.setsockopt(zmq.RCVTIMEO, 2000) #TIMEOUT
                    try:
                        self.socket2.send_string(json.dumps(message), encoding='utf-8')
                        request = self.socket2.recv_string()
                        self.receive_buffer.append(request)
                        print("receive complete")
                    except zmq.ZMQError as e:
                        self.socket2.close()
                        self.socket2 = self.context.socket(zmq.REQ)
                        if e.errno == zmq.EAGAIN:
                            self.send_buffer.append(message)
                        else:
                            print(e)
                            time.sleep(1)
                            self.send_buffer.append(message)

                time.sleep(1)

    def run(self):
        self.establish_connection(5000)

        heart_beats_thread = threading.Thread(target=self.heart_beats, args=[])
        heart_beats_thread.start()

        serv_thread = threading.Thread(target=self.run_server, args=[])
        serv_thread.start()

        client_thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()