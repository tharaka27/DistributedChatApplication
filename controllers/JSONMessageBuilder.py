from asyncio.windows_events import NULL
import json
from re import A
from time import time


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

    def lockIdentity( userId):
        # send peer server {"type" : "lockidentity", "serverid" : "s1", "identity" : "Adel"}
        data = {}
        data[Protocol.typeS.name] = Protocol.lockidentity.name
        #data[Protocol.serverid.name] = serverInfo.getServerId()
        data[Protocol.identity.name] = userId
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
    locked, , 
    , 
    , 
    , 
    ,
    listOf, 
    quitOf, 
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
    
    listserver, , , ,
    authenticate, , rememberme, authresponse, success, reason,
    , notifyusersession, status, alive, managementport, serverup, notifyserverdown,
    , gossip, heartbeatcountlist, startvote, answervote, vote, votedby, suspectserverid,
    startelection, answerelection, coordinator, iamup, viewelection, nominationelection,
    currentcoordinatorid, currentcoordinatoraddress, currentcoordinatorport, currentcoordinatormanagementport'''
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
    former = 30
