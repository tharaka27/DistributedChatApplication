from asyncio.windows_events import NULL
import json
from re import A
from time import time
from tkinter import N


class MessageBuilder:
    __instance = None
    @staticmethod
    def getInstance():
        if MessageBuilder.__instance == None:
            MessageBuilder()
            return MessageBuilder.__instance

    def serverChange(self, approved , serverID):        
        data = {}
        data[Protocol.typeS.name] = Protocol.serverchange.name
        data[Protocol.approved.name] = approved
        data[Protocol.serverid.name] = serverID
        return json.dumps(data)
    
    def route(self,  joiningRoomId ,  host, port=0,  username = None, sessionId = None,  password = None):

        data = {}
        data[Protocol.typeS.name] = Protocol.route.name
        data[Protocol.roomid.name]= joiningRoomId
        data[Protocol.host.name] = host
        data[Protocol.port.name] = port
        if username != None and sessionId != None and password != None:
            data[Protocol.sessionid.name]= sessionId
            data[Protocol.username.name] = username
            data[Protocol.password.name] = password
        return json.dumps(data)


    def message( identity = "",  content = ""):
        data = {}
        data[Protocol.typeS.name] = Protocol.message.name
        data[Protocol.identity.name]= identity
        data[Protocol.content.name] = content
        t = time.localtime()
        data[Protocol.timestamp.name] = time.strftime('%Y-%m-%d %H:%M %Z', time.gmtime(t))
        return json.dumps(data)
    
    def deleteRoom( roomId,  approved) :
        # {"type" : "deleteroom", "roomid" : "jokes", "approved" : "true"}
        data = {}
        data[Protocol.typeS.name] = Protocol.deleteroom.name
        data[Protocol.roomid.name] = roomId
        data[Protocol.approved.name] = approved
        return json.dumps(data)

    def deleteRoomPeers( roomId):
        # {"type" : "deleteroom", "serverid" : "s1", "roomid" : "jokes"}
        data = {}
        data[Protocol.typeS.name] = Protocol.deleteroom.name
        #data[Protocol.serverid.name] = serverInfo.getServerID()
        data[Protocol.roomid.name] = roomId
        return json.dumps(data)

    def releaseRoom( roomId,  approved):
        # "type" : "releaseroomid", "serverid" : "s1", "roomid" : "jokes", "approved":"false"}
        data = {}
        data[Protocol.typeS.name] = Protocol.releaseroomid.name
        #data[Protocol.serverid.name] = serverInfo.getServerID()
        data[Protocol.roomid.name] = roomId
        data[Protocol.approved.name] = approved
        return json.dumps(data)
     
    def lockRoom( roomId):
        #{"type" : "lockroomid", "serverid" : "s1", "roomid" : "jokes"}
        data = {}
        data[Protocol.typeS.name] = Protocol.releaseroomid.name
        #data[Protocol.serverid.name] = serverInfo.getServerID()
        data[Protocol.roomid.name] = roomId
        return json.dumps(data)
    def createRoomResp( roomId,  approved):
        #{"type" : "createroom", "roomid" : "jokes", "approved" : "false"}
        data = {}
        data[Protocol.typeS.name] = Protocol.createroom.name
        data[Protocol.roomid.name] = roomId
        data[Protocol.approved.name] = approved
        return json.dumps(data)

    def whoByRoom(roomId):
        #{ "type" : "roomcontents", "roomid" : "jokes", "identities" : ["Adel","Chenhao","Maria"], "owner" : "Adel" }
        data = {}
        data[Protocol.typeS.name] = Protocol.createroom.name
        data[Protocol.roomid.name] = roomId

        #localChatRoomInfo = serverState.getLocalChatRooms().get(room);
        #membersList = localChatRoomInfo.getMembers()
        #data[Protocol.identities.name] = membersList
        #data[Protocol.owner.name] = localChatRoomInfo.getOwner()
        return json.dumps(data)
    
    def listRooms():
        #{ "type" : "roomlist", "rooms" : ["MainHall-s1", "MainHall-s2", "jokes"] }
        data = {}
        data[Protocol.typeS.name] = Protocol.roomlist.name
        data[Protocol.roomid.name] = roomId

        #roomsList = serverState.getLocalChatRooms().values();
        #data[Protocol.rooms.name] = roomsList
        
        return json.dumps(data)
    
    def listServers():
        '''
                {
                    "type":"serverlist", "servers": [
                                                        {“serverid”:s1, “address”:”192.168.0.3”, ”port”:”4444”}
                                                        {“serverid”:s2, “address”:”192.168.0.2”, ”port”:”4445”}
                                                        {“serverid”:s3, “address”:”192.168.0.1”, ”port”:”4444”}
                                                    ]
                }
        '''

        data = {}
        data[Protocol.typeS.name] = Protocol.serverlist.name
        #servoInfoList = serverState.getServerInfoList()
        #listOfServer = []
        #for server in servoInfoList:
        #    serverData = {}
        #    serverData[Protocol.serverid.name] = server.getServerID()
        #    serverData[Protocol.address.name] = server.getAddress()
        #    serverData[Protocol.port.name] = server.getPort()
        #    listOfServer.append(serverData)
        #data[Protocol.servers.name] = listOfServer

        return json.dumps(data)
    
    def releaseIdentity( userId) :
        #{"type" : "releaseidentity", "serverid" : "s1", "identity" : "Adel"}
        data = {}
        data[Protocol.typeS.name] = Protocol.releaseidentity.name
        #data[Protocol.serverid.name] = serverInfo.getServerId()
        data[Protocol.identity.name] = userId
        return json.dumps(data)

    def lockIdentity( userId, serverID = None, roomId = None,locked = None):
        # send peer server {"type" : "lockidentity", "serverid" : "s1", "identity" : "Adel"}
        data = {}
        data[Protocol.typeS.name] = Protocol.lockidentity.name
        #data[Protocol.serverid.name] = serverInfo.getServerId()
        data[Protocol.identity.name] = userId

        if serverID != None and roomId != None and locked != None:
            data[Protocol.roomid.name] = roomId
            data[Protocol.locked.name] = locked
        return json.dumps(data)

    def newIdentityResp( approve):
        data = {}
        data[Protocol.typeS.name] = Protocol.newidentity.name
        data[Protocol.approved.name] = approve
        return json.dumps(data)

    def roomChange( former,  roomId, identity):
        # {"type" : "roomchange", "identity" : "Maria", "former" : "jokes", "roomid" : "jokes"}
        data = {}
        data[Protocol.typeS.name] = Protocol.roomchange.name
        data[Protocol.identity.name] = identity
        data[Protocol.former.name] = former
        data[Protocol.roomid.name] = roomId
        return json.dumps(data)
    

    def listRoomsClient():
        
        data = {}
        data[Protocol.typeS.name] = Protocol.list.name
        return json.dumps(data)

    def authResponse( success,  reason):
        #{"type":"authresponse", "success":"false", "reason":"null"}
        data = {}
        data[Protocol.typeS.name] = Protocol.authresponse.name
        data[Protocol.success.name] = success
        data[Protocol.reason.name] = reason
        return json.dumps(data)

    def notifyUserSession( username,  sessionId,  status):
        # {"type" : "notifyusersession", "username" : "ray", "sessionid" : "ba64077b-85b4-40f0-a5ac-480ad3e341b3", "serverid", "s1", "status", "login"}
        data = {}
        data[Protocol.typeS.name] = Protocol.notifyusersession.name
        data[Protocol.username.name] = username
        data[Protocol.sessionid.name] = sessionId
        #data[Protocol.serverid.name] = serverInfo.getServerId()
        data[Protocol.status.name] = status
        return json.dumps(data)
    
    
    def makeLoginMessage( username,  password):
        # {"type" : "authenticate", "username" : "ray@example.com", "password":"cheese", "rememberme":"true"}
        data = {}
        data[Protocol.typeS.name] = Protocol.authenticate.name
        data[Protocol.username.name] = username
        data[Protocol.password.name] = password
        data[Protocol.rememberme.name] = "false"
        return json.dumps(data)
    
    def notifyServerDownMessage( serverId):
        # {"type":"notifyserverdown", "serverid":"s2"}
        data = {}
        data[Protocol.typeS.name] = Protocol.notifyserverdown.name
        data[Protocol.serverid.name] = serverId
        return json.dumps(data)

    def serverUpMessage():
        data = {}
        data[Protocol.typeS.name] = Protocol.serverup.name
        #data[Protocol.serverid.name] = serverInfo.getServerId()
        #data[Protocol.address.name] = serverInfo.getAddress()
        #data[Protocol.port.name] = serverInfo.getPort()
        #data[Protocol.managementport.name] = serverInfo.getManagementPort()
        return json.dumps(data)
    
    def startElectionMessage( serverId,  serverAddress,  serverPort = 0, 
            serverManagementPort = 0):
        data = {}
        data[Protocol.typeS.name] = Protocol.startelection.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.address.name] = serverAddress
        data[Protocol.port.name] = str(serverPort)
        data[Protocol.managementport.name] = str(serverManagementPort)
        return json.dumps(data)

    def electionAnswerMessage( serverId,  serverAddress,  serverPort,
            serverManagementPort ):
        data = {}
        data[Protocol.typeS.name] = Protocol.answerelection.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.address.name] = serverAddress
        data[Protocol.port.name] = str(serverPort)
        data[Protocol.managementport.name] = str(serverManagementPort)
        return json.dumps(data)
    
    def setCoordinatorMessage( serverId,  serverAddress,  serverPort, 
            serverManagementPort):
        data = {}
        data[Protocol.typeS.name] = Protocol.coordinator.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.address.name] = serverAddress
        data[Protocol.port.name] = str(serverPort)
        data[Protocol.managementport.name] = str(serverManagementPort)
        return json.dumps(data)

    def gossipMessage( serverId, heartbeatCountList):
        # {"type":"gossip","serverid":"1","heartbeatcountlist":{"1":0,"2":1,"3":1,"4":2}}
        data = {}
        data[Protocol.typeS.name] = Protocol.gossip.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.heartbeatcountlist.name] = heartbeatCountList
        return json.dumps(data)

    def startVoteMessage( serverId,  suspectServerId):
        data = {}
        data[Protocol.typeS.name] = Protocol.startvote.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.suspectserverid.name] = suspectServerId
        return json.dumps(data)

    def answerVoteMessage( suspectServerId,  vote,  votedBy):
        # {"type":"answervote","suspectserverid":"1","vote":"YES", "votedby":"1"}
        data = {}
        data[Protocol.typeS.name] = Protocol.answervote.name
        data[Protocol.suspectserverid.name] = suspectServerId
        data[Protocol.votedby.name] = votedBy
        data[Protocol.vote.name] = vote
        return json.dumps(data)
    
    
    def iAmUpMessage( serverId,  serverAddress,  serverPort, 
            serverManagementPort):
        # {"type":"iamup", "serverid":"1", "address":"localhost", "port":"4444", "managementport":"5555"}
        data = {}
        data[Protocol.typeS.name] = Protocol.iamup.name
        data[Protocol.serverid.name] = serverId
        data[Protocol.address.name] = serverAddress
        data[Protocol.port.name] = str(serverPort)
        data[Protocol.managementport.name] = str(serverManagementPort)
        return json.dumps(data)
    def __init__(self,serverState, serverInfo):
       
        if MessageBuilder.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MessageBuilder.__instance = self
        #serverState = 
        #serverInfo = 

import enum

''' 
     
    , 
    
    , 
    , , 
    , 
    , 
    , 
    ,
    , 
    quit, 
    who, 
    , 
    , 
    , 
    , 
    ,
    lockroomid, 
    , , 
    , 
    
    join
    
    
    movejoin
    
    
    , , '''
class Protocol(enum.Enum):
    typeS = 1
    approved = 2
    serverid = 3
    serverchange = 4

    route = 5
    roomid = 6
    host = 7
    port = 8
    sessionid = 9
    username = 10 
    password = 11

    message = 12
    identity = 13
    content = 14
    timestamp = 15

    deleteroom = 16

    releaseroomid = 17

    createroom = 18

    roomcontents = 19
    identities = 20
    owner = 21

    roomlist = 22
    rooms = 23

    serverlist = 24
    address = 25
    servers = 26

    releaseidentity = 27

    lockidentity = 28

    newidentity = 29

    roomchange = 30
    former = 31

    locked = 32
    list = 33

    authresponse = 34
    success = 35
    reason = 36

    notifyusersession = 37
    status = 38

    authenticate = 39
    rememberme = 40

    notifyserverdown = 41

    serverup = 42
    managementport = 43

    startelection = 44
    answerelection = 45

    coordinator = 46
    iamup = 47 
    viewelection = 48 
    nominationelection = 49
    currentcoordinatorid = 50 
    currentcoordinatoraddress = 51 
    currentcoordinatorport = 52 
    currentcoordinatormanagementport = 53
    listserver = 54
    alive = 55
    gossip = 56 
    heartbeatcountlist= 57 
    startvote = 58
    answervote = 59
    vote = 60
    votedby = 61
    suspectserverid = 62

