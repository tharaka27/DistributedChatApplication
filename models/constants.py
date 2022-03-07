# define all the constants used in the program here

LOCAL_HOST_ADDRESS = "127.0.0.1"

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