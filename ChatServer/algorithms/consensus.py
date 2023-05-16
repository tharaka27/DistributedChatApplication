from http import server
import zmq
from models import serverstate 
from models.serverstate import LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS
import threading
from models.tokens import Gossip, Consensus
import json
import random
import time
from models.constants import CONSENSUS_VOTE_DURATION

 
class Consensus:

    def __init__(self, LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS):
        self.my_server_id = LOCAL_SERVER_CONFIGURATION.getId()
        self.address = LOCAL_SERVER_CONFIGURATION.getAddress()
        self.port = LOCAL_SERVER_CONFIGURATION.getCoordinationPort()
        self.heart_port = LOCAL_SERVER_CONFIGURATION.getHeartPort()
        self.processes = REMOTE_SERVER_CONFIGURATIONS
        self.coord_id = serverstate.COORDINATOR_CONFIGURATION.getId()

    def connect_all(self):
        for p in self.processes:
            if p.getId() != self.my_server_id:
                self.heart_socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getHeartPort()))

    def establish_connection(self):
        self.heart_context = zmq.Context()
        self.heart_socket = self.heart_context.socket(zmq.PUB)
        self.heart_socket.bind('tcp://{}:{}'.format(self.address, self.heart_port))
        self.heart_socket2 = self.heart_context.socket(zmq.SUB)
        heart_timeout = 500*random.randint(4,10)
        self.heart_socket2.setsockopt(zmq.RCVTIMEO, heart_timeout)
        self.connect_all()
        self.heart_socket2.subscribe("")

    def execute(self):
        if (not serverstate.ONGOING_CONSENSUS):
            if (serverstate.COORDINATOR_CONFIGURATION != None):
                serverstate.ONGOING_CONSENSUS = True
                perform_consensus_thread = threading.Thread(target=self.performConsensus, args=[])
                perform_consensus_thread.start()
                serverstate.ONGOING_CONSENSUS = False
        else:
            print("[SKIP] There seems to be on going consensus at the moment, skip.")
    
    def performConsensus(self):
        
        suspectServerId  = None

        # initialise vote set
        serverstate.VOTE_SET[Consensus.Yes] = 0
        serverstate.VOTE_SET[Consensus.No] = 0

        # if I am leader, and suspect someone, I want to start voting to KICK him!
        if (self.coord_id==self.my_server_id):
            for serverId in serverstate.SUSPECT_SERVERS.keys():
                if (serverstate.SUSPECT_SERVERS[serverId] == Gossip.SUSPECTED):
                    suspectServerId = serverId
                    break
            # got a suspect
            if (suspectServerId != None):
                serverstate.VOTE_SET[Consensus.Yes] = 1
                message = {'type' : 'start_vote', 'address': self.address, \
                    'port': self.heart_port, 'id': self.my_server_id, 'suspectServerId': suspectServerId}
                self.heart_socket.send_string(json.dumps(message))
                print(f"Leader calling for vote to kick suspect-server: {message}")
            
                # wait for consensus.vote.duration determined in models.constants
                try:
                    time.sleep(CONSENSUS_VOTE_DURATION)
                except:
                    pass

                # remove server or do nothing
                print(f"Consensus votes to kick server {suspectServerId}: {serverstate.VOTE_SET}")
                if (serverstate.VOTE_SET[Consensus.Yes] > serverstate.VOTE_SET[Consensus.No]):

                    message = {'type' : 'server_down', 'address': self.address, \
                    'port': self.heart_port, 'serverId': suspectServerId}
                    self.heart_socket.send_string(json.dumps(message))

                    serverstate.REMOTE_SERVER_CONFIGURATIONS = [configuration for configuration in serverstate.REMOTE_SERVER_CONFIGURATIONS if configuration.getId() != suspectServerId]
                    serverstate.REMOTE_CHAT_ROOMS = [chatroom for chatroom in serverstate.REMOTE_CHAT_ROOMS if chatroom.getOwner() != suspectServerId]
                    del serverstate.SUSPECT_SERVERS[suspectServerId]
        
        else:
            pass



