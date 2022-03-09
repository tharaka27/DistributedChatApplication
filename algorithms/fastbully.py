import zmq
import time
import parse
import sys
import threading
from models.serverstate import LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS
import json

class Bully:
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
        self.heart_socket2.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        self.connect_all()
        self.heart_socket2.subscribe("")

    def update_coor(self, address, port, id):
        self.coor_ip = address
        self.coor_port = port
        self.coor_id = id 

    def heart_beats(self, proc=None):
        if proc == 'coor':
            while int(self.coor_id) == int(self.id):
                message = {'type' : 'alive', 'address': self.address, \
                    'port': self.heart_port, 'id': self.id }
                self.heart_socket.send_string(json.dumps(message))
                time.sleep(1)
        else:
            while True:
                try:
                    coor_heart_beat = self.heart_socket2.recv_string()
                    request = json.loads(coor_heart_beat)
                    if request['id'] > self.id:
                        print("coordinator  {}".format(coor_heart_beat))
                        self.update_coor(request['address'], request['port'], request['id'])
                
                except:
                    if self.coor_id != self.id:
                        print("Coordinator is dead, get ready for election \n")
                        self.coor_id = -1


    def run_server(self):
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
        while True:
            if self.coor_id == -1:
                try:
                    if self.id == self.maxId:
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