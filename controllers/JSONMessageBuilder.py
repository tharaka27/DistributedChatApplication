from asyncio.windows_events import NULL
import json
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
    


    def __init__(self,serverState, serverInfo):
       
        if MessageBuilder.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MessageBuilder.__instance = self
        #serverState = 
        #serverInfo = 

import enum

''' 
    newidentity 
    , 
    lockidentity
    , 
    locked, , 
    roomchange, 
    former, 
    , 
    releaseidentity,
    listOf, 
    quitOf, 
    who, 
    createroom, 
    roomlist, 
    rooms, 
    roomcontents, 
    identities, 
    owner,
    lockroomid, 
    releaseroomid, 
    deleteroom, 
    , 
    
    join
    
    
    movejoin
    
    listserver, serverlist, servers, address,
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