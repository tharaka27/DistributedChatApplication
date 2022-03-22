from .chatroominfo import ChatRoomInfo
from .configuration import ServerConfiguration
from .localroominfo import LocalRoomInfo
from .message import Message
from .remoteroominfo import RemoteRoomInfo
from .userSession import UserSession


# create this server's configuration
global LOCAL_SERVER_CONFIGURATION 
LOCAL_SERVER_CONFIGURATION = ServerConfiguration("DEFAULT", "localhost", "5000", "5000", "5000", 1)

# list of configurations of other servers 
REMOTE_SERVER_CONFIGURATIONS = []

# list of chat rooms in this server
LOCAL_CHAT_ROOMS = []

# list of remote chat rooms in other servers
REMOTE_CHAT_ROOMS = []

# list of users connected to this server
LOCAL_USERS = []

# set if this server is coordinator
AMICOORDINATOR = False

# set is coordinator is not alive
ISCOORDINATORALIVE = False


# set coordinator ip and port
COORDINATOR = { "ip" : "", "port":"" }

# List of all the users in the system
ALL_USERS = []

ONGOING_CONSENSUS = False

COORDINATOR_CONFIGURATION = ServerConfiguration("DEFAULT", "localhost", "5000", "5000", "5000", 1)

# dict of (token.CONSENSUS, Integer)
VOTE_SET = dict()

# list of suspect servers
SUSPECT_SERVERS = dict()  # dict of (serverId, token.Gossip)
