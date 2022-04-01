import zmq
import time
import parse
import sys
import threading
#from models.serverstate import LOCAL_SERVER_CONFIGURATION, REMOTE_SERVER_CONFIGURATIONS
from models import serverstate
import json
import random
from controllers.JSONMessageBuilder import MessageBuilder
from models.localroominfo import LocalRoomInfo

class FastBully:

    global Fast_enabled, coord_dead, election_started, send_iamUP, view_expected, current_cord, other_servers_view,proc
    global room_list
    other_servers_view = False
    send_iamUP = False
    current_cord = -1
    view_expected = False
    Fast_enabled = True
    coord_dead = False
    election_started = False
    _instance = None
    proc = None
    room_list = []

    def __init__(self):
        if FastBully._instance != None:
            raise Exception("This is a singleton class") 
        else:
            FastBully._instance = self
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
        self.heart_beat_queue = []
        self.server_queue = []
        self.msg_builder = MessageBuilder.getInstance()
        for p in self.processes:
            print(p)
            if self.max_id < p.getId():
                self.max_id = p.getId()
        print("[Configuration] ip:{} coor:{} heart:{}".format(self.address, self.port, self.heart_port))
    
    @staticmethod
    def getInstance():
        if FastBully._instance == None:
            FastBully()
        return FastBully()._instance

    def connect_to_higher_ids(self):
        for p in self.processes:
            # changed to connect all
            if p.getId() > int(self.id):
                self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
        # so that last process does not block on send...
        #self.socket2.connect('tcp://{}:{}'.format(p['ip'], 55555))
    
    def connect_all_heart(self):
        for p in self.processes:
            if p.getId() != self.id:
                self.heart_socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getHeartPort()))

    def connect_all(self):
        for p in self.processes:
            if p.getId() != self.id:
                self.socket_all.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort()))

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

        self.socket_coor = self.context.socket(zmq.REQ)
        self.socket_coor.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        

        self.socket_all = self.context.socket(zmq.REQ)
        self.socket_all.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        self.connect_all()

        self.socket_list = self.context.socket(zmq.REQ)
        self.socket_list.setsockopt(zmq.RCVTIMEO, TIMEOUT)

        self.heart_context = zmq.Context()
        self.heart_socket = self.heart_context.socket(zmq.PUB)
        self.heart_socket.bind('tcp://{}:{}'.format(self.address, self.heart_port))
        self.heart_socket2 = self.heart_context.socket(zmq.SUB)
        heart_timeout = 500*random.randint(6,10)
        self.heart_socket2.setsockopt(zmq.RCVTIMEO, heart_timeout)
        self.connect_all_heart()
        self.heart_socket2.subscribe("")

    def update_coor(self, address, port, id):
        self.coor_ip = address
        self.coor_port = port
        self.coor_id = id 

    def heart_beats(self):

        global Fast_enabled,coord_dead,election_started, send_iamUP,view_expected, current_cord,other_servers_view,proc

        first_time = True

        while True:

            if proc == 'coor':

                while proc == 'coor':

                    task_instance = ""
                    if not(len(self.task_list)== 0):
                        task_instance = self.task_list.pop(0)
                    message = {'type' : 'alive', 'address': self.address, \
                        'port': self.heart_port, 'id': self.id, 'task' : task_instance }
                    self.heart_socket.send_string(json.dumps(message))
                    
                    if coord_dead:
                        coord_dead = False

                    if election_started:
                        election_started = False  
                    
                    serverstate.AMICOORDINATOR = True
                    serverstate.ISCOORDINATORALIVE = True
                    time.sleep(1)

            else:

                while proc != 'coor':
                    
                    if send_iamUP :
                        print("[INFO] Send I am up to other servers")
                        message = {'type' : 'IamUp'}
                        self.heart_socket.send_string(json.dumps(message)) 
                        send_iamUP = False
                        time.sleep(1)

                    else: 
                        try:

                            coor_heart_beat = self.heart_socket2.recv_string()
                            request = json.loads(coor_heart_beat)
                            self.heart_beat_queue.append(request)

                        except:
                            if (first_time):
                                first_time = False
                                continue
                            else:
                                if view_expected:
                                    print("[INFO] No view message received form others...So iam the coordinator")
                                    view_expected = False
                                    current_cord = self.id
                                    other_servers_view = True
                                    proc='coor'
                                    

                                # other process has already started election
                                elif (election_started):
                                    print("[INFO] Election is in process...")
                                    serverstate.ISCOORDINATORALIVE = False
                                    try:
                                        coor_heart_beat = self.heart_socket2.recv_string()
                                        request = json.loads(coor_heart_beat)
                                        self.heart_beat_queue.append(request)
                                    except:
                                        coord_dead =True

                                # I am the first to detect the failure
                                elif self.coor_id != self.id:
                                    if not(view_expected) and not(election_started):
                                        coord_dead = True
                                        # Send dead message
                                        message = {'type' : 'dead' }
                                        self.heart_socket.send_string(json.dumps(message))
                                        election_started = True
                                        print("[INFO] Coordinator is dead, get ready for election")
                                        #self.start_election()
                                        serverstate.ISCOORDINATORALIVE = False

                                first_time = True

############################################ Get rooms for list message ########################################
    def get_rooms(self):

        alive_servers = []
        alive_servers.append(serverstate.LOCAL_SERVER_CONFIGURATION.getServerName())

        alive_p_address=""
        alive_p_port=""

        for p in self.processes:

            # connect to servers and check weather they are alive
            if p.getId() < int(self.id):

                print("\n[INFO] Sending Check alive message to :",p.getId())
                self.socket_list = self.context.socket(zmq.REQ)
                self.socket_list.setsockopt(zmq.RCVTIMEO, 3000) #TIMEOUT
                self.socket_list.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))

                list_message = {"type":"check_alive"}
                

                try:
                    self.socket_list.send_string(json.dumps(list_message))
                    res = self.socket_list.recv_string()
                    response = json.loads(res)
                    alive_servers.append(p.getServerName())
                    alive_p_address = p.getAddress()
                    alive_p_port = p.getCoordinationPort()
                    print("[INFO] Recived a response for check alive message")

                except Exception as e:
                    print("[INFO] Did not recieved a rersponse for check alive message")
                    continue

        existing_rooms = []

        for room in serverstate.ALL_CHAT_ROOMS:

            room_server = room.getCoordinator()
            if room_server in alive_servers:
                existing_rooms.append(room.getChatRoomId())
            else:
                serverstate.ALL_CHAT_ROOMS.remove(room)
                task = {"type":"deleteroom","serverid":room_server,"roomid":room.getChatRoomId()}
                self.task_list.append(task)

                room_members = room.getMembers()

                for m in room_members:
                    task2 = {"type":"quit","identity":m}
                    self.task_list.append(task2)
        
        # add main halls
        for s in alive_servers:
            main_hall = "MainHall-"+s
            existing_rooms.append(main_hall)
        
        print("returned")
        return existing_rooms




############################################ ELECTION ###########################################################   

    def start_election(self):

        #self.declare_am_coordinator()
        global coord_dead

        res_ids = []
        coordinator_found = False
        accepted = False
        # Get process with higher priority than self

        while ((not coordinator_found) and coord_dead):

            if self.id == self.max_id:
                print("[INFO] I am the highest priority..So I am the Coordinator")
                self.declare_am_coordinator()
                coordinator_found = True
                serverstate.ISCOORDINATORALIVE = True

            else: # goes if self.id < self.maxID

                print("[INFO] high prority id range :",self.id," to ",self.max_id)

                elec_message = {'type' : 'election'}

                for p in self.processes:

                    # changed to connect all
                    if p.getId() > int(self.id):

                        print("\n[INFO] Sending election message to server with priority :",p.getId())
                        self.socket2 = self.context.socket(zmq.REQ)
                        self.socket2.setsockopt(zmq.RCVTIMEO, 3000) #TIMEOUT
                        self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
                        try:
                            self.socket2.send_string(json.dumps(elec_message))
                            res = self.socket2.recv_string()
                            response = json.loads(res)
                            res_ids.append(response['id'])
                            print("[INFO] Recived a response for election message")

                        except:
                            print("[INFO] Did not recieved a rersponse for election message")
                            continue
                            
                            
                print("[INFO] Number of candidates for coordinator ->",len(res_ids))

                if (len(res_ids)> 0 and coord_dead):

                    # Send nomination
                    while ((len(res_ids) > 0) and (not(accepted)) and (coord_dead)):

                        selected_cord = max(res_ids)
                        message = {'type' : 'nomination','id':selected_cord}
                        print("[INFO] Selected coordinator :",selected_cord)

                        for p in self.processes:

                            # changed to connect all
                            if p.getId() == selected_cord:

                                self.socket2 = self.context.socket(zmq.REQ)
                                self.socket2.setsockopt(zmq.RCVTIMEO, 3000) #TIMEOUT
                                self.socket2.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort() ))
                                try:
                                    print("\n[INFO] Sending nomination to the selected server")
                                    self.socket2.send_string(json.dumps(message))
                                    res2 = self.socket2.recv_string()
                                    response2 = json.loads(res2)
                                    print(response2)
                                    if(response2['type'] == "coordinator" and response2['status'] == "accepted"):
                                        print("[INFO] Candidate accepted nomination")
                                        print("[INFO] New coordinator appointed !")
                                        coordinator_found = True
                                        accepted = True
                                        return True

                                except:
                                    print("[INFO] Nomination was not accepted by the candidate")
                                    print("[INFO] Moving to next candidate")
                                    continue

                        res_ids.remove(selected_cord)
                    
                    if not(coord_dead):
                        return True


                else:
                    print("[INFO] No higher priority process to be coordinator")
                    self.declare_am_coordinator()
                    coordinator_found = True
                    return True

        return True
    
############################################ SERVER ###########################################################

    def run_server(self):

        global proc,election_started,coord_dead,room_list

        while True:
            try:
                request = self.socket.recv_string()
                
                req = json.loads(request)

                print("[INFO] Request of type ",req['type']," arrived")

                if req['type']=='election':
                    print("[INFO] election message recived",self.id)
                    #respond alive..with id
                    message = {'type' : 'Iam_alive','id': self.id}
                    self.socket.send_string(json.dumps(message)) 

                elif req['type'] == 'recover':
                    print("[INFO] Recover message recived")
                    message = {"type":"recover_ok"}
                    self.socket.send_string(json.dumps(message))  
                    print("[INFO] recover ok message sent")

                elif req['type'] == 'IamUp': 
                    print("[INFO] Iam up message recived from a new server")

                    room_data = []

                    for room in serverstate.ALL_CHAT_ROOMS:
                        room_data.append(room.__dict__)

                    message = {'type' : 'view','current_cod':self.coor_id,'rooms':room_data,'ids':serverstate.ALL_USERS}
                    self.socket.send_string(json.dumps(message))  
                    print("[INFO] View message sent")
                
                elif req['type'] == 'check_alive':
                    print("[INFO] Check alive message recived")    
                    message = {"type":"Iam_alive"}
                    self.socket.send_string(json.dumps(message))  
                    print("[INFO] I am alive message sent")

                elif req['type'] == 'get_list':
                    print("[INFO] Get room list message recived")  
                    room_list = self.get_rooms()
                    reply = {"type":"list_ok"}
                    self.socket.send_string(json.dumps(reply)) 
                    print("[INFO] Searching rooms complete")
                
                elif req['type'] == 'send_list':
                    print("[INFO] Send room list message recived")  
                    reply = {"type":"room_list", "rooms":room_list}
                    self.socket.send_string(json.dumps(reply)) 
                    print("[INFO] Sent rooms list")                    

                elif req['type'] == 'Iam_Coord': 
                    #cord_msg = {"type" : "Iam_Coord","id": self.id, "address":self.address, "port":self.port}
                    print("[INFO] New coordinator message received")
                    message = {'type' : 'updated'}
                    self.socket.send_string(json.dumps(message)) 
                    self.coor_id = req['id']  
                    self.update_coor(req['address'], req['port'], int(req['id']))
                    serverstate.AMICOORDINATOR = False
                    serverstate.ISCOORDINATORALIVE = True    
                    election_started = False
                    coord_dead = False
                    proc = None 
                    print("[INFO] Coordinator updated")               
                
                elif req['type']=='nomination':
                    print("[INFO] Nomination received")
                    if req['id'] == self.id:
                        print("[INFO] Accepted nomination")
                        message = {'type' : 'coordinator','status': "accepted"}
                        self.socket.send_string(json.dumps(message))
                        self.declare_am_coordinator()
                    else:
                        print("[INFO] Nomination was not intended to me")
                        message = {'type' : 'coordinator','status': "rejected"}
                        self.socket.send_string(json.dumps(message))
                
                elif req['type'] == 'create_identity' and self.id == self.coor_id:
                    print("[INFO] Received create identity task")
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

                    print("[INFO] Received create room task")
                    isRoomExist = False
                    for room in serverstate.ALL_CHAT_ROOMS:
                        if room.getChatRoomId() == req['roomid']:
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
                        
                        message = { "type" : "create_chat_room" , "identity" : req['identity'],\
                            "server": req["server"], "roomid" : req['roomid']}
                        self.task_list.append(message)
                                
                        self.socket.send_string(self.msg_builder.createNewChatRoom(True)) 
                    else:
                        self.socket.send_string(self.msg_builder.createNewChatRoom(False)) 

                elif req['type'] == 'deleteroom' and self.id == self.coor_id:

                    print("[INFO] Received delete room task")

                    roomid = req['roomid']
                    serverid = req['serverid']
                    deleted = False

                    for r in serverstate.ALL_CHAT_ROOMS:
                                    
                        r_id = r.getChatRoomId()

                        if r_id == roomid:
                            serverstate.ALL_CHAT_ROOMS.remove(r)
                            deleted = True
                            break

                    # send message to all servers through pub-sub scheme

                    if(deleted):
                        self.task_list.append({"type" : "deleteroom","serverid": serverid,"roomid":roomid})
                        self.socket.send_string(self.msg_builder.approved(True)) 
                        print("[INFO] Room deleted")
                    else:
                        self.socket.send_string(self.msg_builder.approved(False)) 
                        print("[INFO] No room found with requested ID")
                
                elif req['type'] == 'quit' and self.id == self.coor_id:

                    print("[INFO] Received quit task")

                    id = req['identity']

                    deleted = False

                    for u in serverstate.ALL_USERS:

                        if u == id:
                            serverstate.ALL_USERS.remove(u)
                            deleted = True
                            break

                    # send message to all servers through pub-sub scheme

                    if(deleted):
                        self.task_list.append({"type" : "quit","identity": id})
                        self.socket.send_string(self.msg_builder.approved(True)) 
                        print("[INFO] Identity deleted")
                    else:
                        self.socket.send_string(self.msg_builder.approved(False)) 
                        print("[INFO] No identity found with requested ID")

                else:
                    self.socket.send_string(self.msg_builder.errorServer())

            except json.decoder.JSONDecodeError as e:
                print("[Warning] Trying to decode election message")
            
            except zmq.ZMQError as e:
                
                self.socket.close()
                self.socket = self.context.socket(zmq.REP)
                self.socket.bind('tcp://{}:{}'.format(self.address, self.port))
            

################################# DECLARE COORDINATOR #########################################################
  
    def declare_am_coordinator(self):

        global proc,election_started,coord_dead

        print('[INFO] I am the coordinator')
        
        serverstate.AMICOORDINATOR = True
        serverstate.ISCOORDINATORALIVE = True
        self.update_coor(self.address, self.heart_port, self.id)
        proc='coor'
        election_started = False
        coord_dead = False


        cord_msg = {"type" : "Iam_Coord","id": self.id, "address":self.address, "port":self.port}

        for p in self.processes:
            if p.getId() != self.id:
                self.socket_all = self.context.socket(zmq.REQ)
                self.socket_all.setsockopt(zmq.RCVTIMEO, 3000)
                self.socket_all.connect('tcp://{}:{}'.format(p.getAddress(), p.getCoordinationPort()))
                try:
                    print("\n[INFO] Sending I am Coordinator meesage to server with id ->",p.getId())
                    self.socket_all.send_string(json.dumps(cord_msg))
                    req = self.socket_all.recv_string()
                    print("[INFO] Response Received")
                except Exception as e:
                    print("[INFO] No reply received")
                    print("[Warining] ",e)


############################################ CLIENT ###########################################################

    def run_client(self):

        global coord_dead, send_iamUP, view_expected, current_cord,other_servers_view
        updated = False
        iamup_sent = False

        while True:

            if coord_dead and updated:
                print("[INFO] calling election")
                result = self.start_election() 
                if result:
                    coord_dead = False
            

            if not(updated):

                if not(iamup_sent):
                    send_iamUP = True
                    message = {'type' : 'IamUp'}
                    self.send_buffer.append(message)
                    iamup_sent = True
                    view_expected = True
                
                if other_servers_view:
                    other_servers_view = False
                    updated = True
                    view_expected = False
                    if current_cord <= self.id:
                        self.declare_am_coordinator()


            time.sleep(0.5)

#################################### message sender ####################################################
    def run_msg_sender(self):

        global current_cord,other_servers_view,view_expected

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
                    
                    print("[INFO] Trying to send message to the coordinator ({},{})".format(\
                        address,port), message)

                    #get list message
                    if message['type'] == 'get_list':
                        
                        try:
                            self.socket_coor = self.context.socket(zmq.REQ)
                            self.socket_coor.setsockopt(zmq.RCVTIMEO, 3000)
                            self.socket_coor.connect('tcp://{}:{}'.format(address, port))
                            self.socket_coor.send_string(json.dumps(message))
                            req = self.socket_coor.recv_string()

                            r = json.loads(req)
                            if r['type'] == 'list_ok':
                                print("[INFO] List ok message recieved")
                                try:
                                    req_msg = {"type":"send_list"}
                                    self.socket_coor.send_string(json.dumps(req_msg))
                                    print("[INFO] Send list message sent")
                                    res = self.socket_coor.recv_string()
                                    print("[INFO] Rooms recived")
                                    self.receive_buffer.append(res)
                                except:
                                    self.socket_coor.close(0)
                                    self.socket_coor = self.context.socket(zmq.REQ)
                                    self.socket_coor.setsockopt(zmq.RCVTIMEO, 2000)
                                    self.send_buffer.append(message)

                            print("[INFO] Receive complete")
                            
                        except zmq.ZMQError as e:

                            # try restarting the socket connection
                            self.socket_coor.close(0)
                            self.socket_coor = self.context.socket(zmq.REQ)
                            self.socket_coor.setsockopt(zmq.RCVTIMEO, 2000)
                            self.socket_coor.connect('tcp://{}:{}'.format(address, port))

                            try:
                                print("[INFO] List ok message recieved")
                                req_msg = {"type":"send_list"}
                                self.socket_coor.send_string(json.dumps(req_msg))
                                print("[INFO] Send list message sent")
                                res = self.socket_coor.recv_string()
                                print("[INFO] Rooms recived")
                                self.receive_buffer.append(res)
                            except:
                                self.socket_coor.close(0)
                                self.socket_coor = self.context.socket(zmq.REQ)
                                self.socket_coor.setsockopt(zmq.RCVTIMEO, 2000)
                                self.send_buffer.append(message)

                    # other types of messages
                    else:

                        try:
                            self.socket_coor = self.context.socket(zmq.REQ)
                            self.socket_coor.setsockopt(zmq.RCVTIMEO, 3000)
                            self.socket_coor.connect('tcp://{}:{}'.format(address, port))
                            self.socket_coor.send_string(json.dumps(message))
                            req = self.socket_coor.recv_string()

                            r = json.loads(req)
                            if r['type'] == 'view':
                                print("[INFO] View message recived from a Other server")
                                print("[INFO] Current view of the system :",r)

                                if view_expected:
                                    current_cord = r['current_cod']

                                    for room in r['rooms']:

                                        room_instance = LocalRoomInfo()
                                        room_instance.setChatRoomID(room["ChatRoomId"])
                                        room_instance.setOwner(room["owner"])
                                        room_instance.setCoordinator(room["coordinator"])
                                        room_instance.setMembers(room["members"])
                                        serverstate.ALL_CHAT_ROOMS.append(room_instance)
                                    
                                    serverstate.ALL_USERS = r["ids"]
                                    
                                    print("[INFO] Users and rooms updated from view message")
                                    other_servers_view = True
                                    view_expected = False

                            else:
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

############################ Heart beat request Processor #############################
    def heartBeat_rq_processor(self):

        global Fast_enabled,coord_dead,election_started, send_iamUP,view_expected, current_cord,other_servers_view

        while True:

            if (len(self.heart_beat_queue) == 0 ):
                continue
            else:

                request = self.heart_beat_queue.pop(0)
            
                # if heart beat message
                if(request['type'] == "alive"):
                    print("coordinator  {}".format(request))
                    serverstate.ISCOORDINATORALIVE = True
                    self.update_coor(request['address'], request['port'], int(request['id'])) 
                    if election_started:
                        election_started = False  

                    # check whether their is a task
                    if not(request['task'] == ''):

                        # handle create_identity task
                        if request['task']['type'] == 'create_identity':

                            if not(request['task']["identity"] in serverstate.ALL_USERS) :
                                serverstate.ALL_USERS.append(request['task']["identity"])
                                print("[INFO] Added new user {} to the ALL_USERS ".format(\
                                    request['task']["identity"]))
                        
                        elif request['task']['type'] == 'create_chat_room':

                            roomid = request['task']['roomid']
                            isRoomExist = False
                            for room in serverstate.ALL_CHAT_ROOMS:
                                if room.getChatRoomId() == roomid:
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
                        
                        elif request['task']['type'] == 'deleteroom':
                            
                            roomid = request['task']['roomid']

                            for r in serverstate.ALL_CHAT_ROOMS:
                                
                                r_id = r.getChatRoomId()

                                if r_id == roomid:
                                    serverstate.ALL_CHAT_ROOMS.remove(r)
                                    break
                            
                            print("[INFO] removed chatroom {} from server".format(\
                                    request['task']["roomid"]))
                        
                        elif request['task']['type'] == 'quit':
                            
                            id = request['task']['identity']

                            for u in serverstate.ALL_USERS:

                                if u == id:
                                    serverstate.ALL_USERS.remove(u)
                                    break
                            
                            print("[INFO] removed identity {} from server".format(\
                                    request['task']["identity"])) 

                # if coordinator dead message                        
                elif (request['type'] == "dead"):
                    print("[INFO] Coordinator dead messsage recieved")
                    election_started = True
                    serverstate.ISCOORDINATORALIVE = False
                
                # I am up message 
                elif (request['type'] == "IamUp"):
                    print("[INFO] Iam up message recived from a new server")

                    room_data = []

                    for room in serverstate.ALL_CHAT_ROOMS:
                        room_data.append(room.__dict__)

                    message = {'type' : 'view','current_cod':self.coor_id,'rooms':room_data,'ids':serverstate.ALL_USERS}
                    self.heart_socket.send_string(json.dumps(message))  
                    print("[INFO] View message sent")

                # View message
                elif (request['type'] == "view"):

                    print("[INFO] View message recived from a Other server")
                    print("[INFO] Current view of the system :",request)

                    if view_expected:

                        current_cord = request['current_cod']

                        for room in request['rooms']:
                            room_instance = LocalRoomInfo()
                            room_instance.setChatRoomID(room["ChatRoomId"])
                            room_instance.setOwner(room["owner"])
                            room_instance.setCoordinator(room["coordinator"])
                            room_instance.setMembers(room["members"])
                            serverstate.ALL_CHAT_ROOMS.append(room_instance)
                        
                        serverstate.ALL_USERS = request["ids"]

                        print("[INFO] Users and rooms updated from view message")
                        
                        other_servers_view = True
                        view_expected = False

                else:
                    print("[INFO] Unkown message")

    # def server_Msg_queue(self):


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

        heart_beat_message_reader = threading.Thread(target=self.heartBeat_rq_processor, args=[])
        heart_beat_message_reader.start()

