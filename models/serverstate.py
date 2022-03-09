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