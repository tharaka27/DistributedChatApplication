import zmq
import time
import parse
import sys
import threading
from models.serverstate import LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS
import json
import random

class Bully:

    global Fast_enabled, coord_dead, election_started
    Fast_enabled = True
    coord_dead = False
    election_started = False

    def __init__(self, LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS):
        self.max_id = LOCAL_SERVER_CONFIGURATION.getId()
        self.address = LOCAL_SERVER_CONFIGURATION.getAddress()
        self.port = LOCAL_SERVER_CONFIGURATION.getCoordinationPort()
        self.heart_port = LOCAL_SERVER_CONFIGURATION.getHeartPort()
        self.processes = REMOTE_SERVER_CONFIGURATIONS
        self.id = LOCAL_SERVER_CONFIGURATION.getId()
        self.coor_id = -1
        for p in self.processes:
            print(p)
            if self.max_id < p.getId():
                self.max_id = p.getId()
        print("---------------------\n Max ID is" + str(self.max_id))

    def connect_to_higher_ids(self):
        for p in self.processes:
            if p.getId() > int(self.id):
                self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
        # so that last process does not block on send...
        #self.socket2.connect('tcp://{}:{}'.format(p['ip'], 55555))
    
    def connect_all(self):
        for p in self.processes:
            if p.getId() != self.id:
                self.heart_socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getHeartPort()))

    def establish_connection(self, TIMEOUT):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
        self.socket2 = self.context.socket(zmq.REQ)
        self.socket2.setsockopt(zmq.RCVTIMEO, TIMEOUT)
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
                            self.update_coor(request['address'], request['port'], request['id']) 
                            if election_started:
                                election_started = False   

                        # if coordinator dead message                        
                        elif (request['type'] == "dead"):
                            print("election is in process...")
                            election_started = True

                        else:
                            print("Unkown message")
                        

                    else:
                        if request['id'] > self.id:
                            print("coordinator  {}".format(coor_heart_beat))
                            self.update_coor(request['address'], request['port'], request['id'])
                
                except:
                    if Fast_enabled:

                        # other process has already started election
                        if (election_started):
                            print("election is in process...")
                        
                        # I am the first to detect the failure
                        elif self.coor_id != self.id:
                            coord_dead = True
                            # Send dead message
                            message = {'type' : 'dead' }
                            self.heart_socket.send_string(json.dumps(message))
                            election_started = True
                            print("Coordinator is dead, get ready for election \n")
                            #self.start_election()
                    

                    else:
                        if self.coor_id != self.id:
                            print("Coordinator is dead, get ready for election \n")
                            self.coor_id = -1
                        
    def start_election(self):

        #self.declare_am_coordinator()

        res_ids = []
        coordinator_found = False
        # Get process with higher priority than self

        while (not coordinator_found):

            if self.id == self.max_id:
                print(" iam the highest")
                self.declare_am_coordinator()
                coordinator_found = True

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
                    print("inside loop saho")
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

    
        else:

            while True:
                request = self.socket.recv_string()
                if request.startswith('election'):
                    #respond alive..
                    self.socket.send_string('alive')
    
    def declare_am_coordinator(self):
        print('I am the coordinator')
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
                        
                time.sleep(1)

    def run(self):
        self.establish_connection(2000)

        heart_beats_thread = threading.Thread(target=self.heart_beats, args=[])
        heart_beats_thread.start()

        serv_thread = threading.Thread(target=self.run_server, args=[])
        serv_thread.start()

        client_thread = threading.Thread(target=self.run_client, args=[])
        client_thread.start()