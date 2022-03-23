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

    global Fast_enabled, coord_dead, election_started, send_iamUP, view_expected, current_cord, other_servers_view
    other_servers_view = False
    send_iamUP = False
    current_cord = -1
    view_expected = False
    Fast_enabled = True
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

        global Fast_enabled,coord_dead,election_started, send_iamUP,view_expected, current_cord,other_servers_view

        if proc == 'coor':
            while int(self.coor_id) == int(self.id):
                
                message = {'type' : 'alive', 'address': self.address, \
                    'port': self.heart_port, 'id': self.id }
                self.heart_socket.send_string(json.dumps(message))
                
                if coord_dead:
                    coord_dead = False

                if election_started:
                    election_started = False  
                
                serverstate.AMICOORDINATOR = True
                serverstate.ISCOORDINATORALIVE = True
                time.sleep(1)
        else:
            while True:

                if send_iamUP :
                    print("I am up sent")
                    message = {'type' : 'IamUp'}
                    self.heart_socket.send_string(json.dumps(message)) 
                    send_iamUP = False
                    view_expected = True
                    time.sleep(1)

                else: 
                    try:
                        coor_heart_beat = self.heart_socket2.recv_string()
                        request = json.loads(coor_heart_beat)

                        if Fast_enabled :
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
                                print("dead sent")
                                election_started = True
                                serverstate.ISCOORDINATORALIVE = False
                            
                            # I am up message 
                            elif (request['type'] == "IamUp"):
                                print("Someone is up again heart beat",self.coor_id)
                                message = {'type' : 'view','current_cod':self.coor_id}
                                self.heart_socket.send_string(json.dumps(message))  

                            # View message
                            elif (request['type'] == "view"):
                                print("view recived from Others...")

                                if view_expected:
                                    current_cord = request['current_cod']
                                    other_servers_view = True
                                    view_expected = False

                            else:
                                print("Unkown message")
                            
                
                    except:

                        if Fast_enabled:
  
                            if view_expected:
                                print("no view message recived form others...So iam the coordinator")
                                view_expected = False
                                current_cord = self.id
                                other_servers_view = True
                                

                            # other process has already started election
                            elif (election_started):
                                print("election is in process...")
                                serverstate.ISCOORDINATORALIVE = False

                            # I am the first to detect the failure
                            elif self.coor_id != self.id:

                                if not(view_expected):
                                    coord_dead = True
                                    # Send dead message
                                    message = {'type' : 'dead' }
                                    self.heart_socket.send_string(json.dumps(message))
                                    election_started = True
                                    print("Coordinator is dead, get ready for election \n")
                                    #self.start_election()
                                    serverstate.ISCOORDINATORALIVE = False
                        
############################################ ELECTION ###########################################################   

    def start_election(self):

        #self.declare_am_coordinator()

        res_ids = []
        coordinator_found = False
        accepted = False
        # Get process with higher priority than self

        while (not coordinator_found):

            if self.id == self.max_id:
                print(" i am the highest")
                self.declare_am_coordinator()
                coordinator_found = True
                serverstate.ISCOORDINATORALIVE = True

            else: # goes if self.id < self.maxID

                self.connect_to_higher_ids()
                print(self.id,self.max_id)
                for i in range (self.id+1,self.max_id+1):

                    elec_message = {'type' : 'election','id':id}
                    
                    try:
                        self.socket2.send_string(json.dumps(elec_message))
                        res = self.socket2.recv_string()
                        response = json.loads(res)
                        print(response['id'])
                        res_ids.append(response['id'])

                    except:
                            continue
                            
                            

                if (len(res_ids)> 0):

                    print("athule bosa :",len(res_ids))

                    # Send nomination
                    while len(res_ids) > 0 and not(accepted):

                        selected_cord = max(res_ids)
                        message = {'type' : 'nomination','id':selected_cord}

                        for i in range (0,len(res_ids)):
                            try:
                                self.socket2.send_string(json.dumps(message))
                                res2 = self.socket2.recv_string()
                                response2 = json.loads(res2)
                                if(response2['type'] == "coordinator" and response2['status'] == "accepted"):
                                    print("New coordinator appointed !")
                                    coordinator_found = True
                                    accepted = True
                                    break

                            except:
                                # Previous process did not respond
                                break

                        res_ids.remove(selected_cord)
                else:
                    print("No higher IDs")
                    self.declare_am_coordinator()
                    coordinator_found = True
        return True

    
############################################ SERVER ###########################################################

    def run_server(self):

        global Fast_enabled

        if (Fast_enabled):

            while True:
                try:
                    request = self.socket.recv_string()
                    print("request recived")
                    req = json.loads(request)
                    if req['type']=='election':
                        #respond alive..with id
                        message = {'type' : 'alive','id': self.id}
                        self.socket.send_string(json.dumps(message))                
                    
                    elif req['type']=='nomination':
                        if req['id'] == self.id:
                            message = {'type' : 'coordinator','status': "accepted"}
                            self.socket.send_string(json.dumps(message))
                            self.declare_am_coordinator()
                        else:
                            message = {'type' : 'coordinator','statues': "rejected"}
                            self.socket.send_string(json.dumps(message))
                    
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

                except json.decoder.JSONDecodeError as e:
                    print("[Warning] Trying to decode election message")
                
                except zmq.ZMQError as e:
                    
                    self.socket.close()
                    self.socket = self.context.socket(zmq.REP)
                    self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
                

################################# DECLARE COORDINATOR #########################################################
  
    def declare_am_coordinator(self):
        print('I am the coordinator')
        serverstate.AMICOORDINATOR = True
        serverstate.ISCOORDINATORALIVE = True
        self.update_coor(self.address, self.heart_port, self.id)
        heart_beats_thread = threading.Thread(target=self.heart_beats, args=['coor'])
        heart_beats_thread.start()

############################################ CLIENT ###########################################################

    def run_client(self):

        global coord_dead, send_iamUP, view_expected, current_cord,other_servers_view
        updated = False
        iamup_sent = False

        if Fast_enabled:

            while True:

                if coord_dead and updated:
                    print("calling election")
                    result = self.start_election() 
                    if result:
                        coord_dead = False

                # if not empty send message
                if not(len(self.send_buffer) == 0 or self.coor_id == -1):

                    message = self.send_buffer.pop(0)
                    print("[INFO] Trying to send message", message)
                    self.connect_to_coordinator()
                    self.socket2.setsockopt(zmq.RCVTIMEO, 5000) #TIMEOUT

                    try:

                        print("send string")
                        self.socket2.send_string(json.dumps(message), encoding='utf-8')
                        #time.sleep(1)
                        request = self.socket2.recv_string()
                        print("receive complete")
                        self.receive_buffer.append(request)
                        
                    except zmq.ZMQError as e:

                        if e.errno == zmq.EAGAIN:
                            self.send_buffer.append(message)
                        print(e)

                if not(updated):

                    if not(iamup_sent):
                        send_iamUP = True
                        iamup_sent = True
                    
                    if other_servers_view:
                        other_servers_view = False
                        updated = True
                        if current_cord <= self.id:
                            self.declare_am_coordinator()

                time.sleep(0.5)

    def run(self):
        self.establish_connection(5000)

        heart_beats_thread = threading.Thread(target=self.heart_beats, args=[])
        heart_beats_thread.start()

        serv_thread = threading.Thread(target=self.run_server, args=[])
        serv_thread.start()

        client_thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()

