from models.serverstate import LOCAL_USERS
from models.userSession import UserSession
from controllers.JSONMessageBuilder import MessageBuilder

class newIdentityProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "newidentity"
        self._name = json_data["identity"]
        
    def handle(self):
        # check for the availability of name

        if self._name == "Tharaka":
            LOCAL_USERS.append( UserSession(self._name, "Default", "Default", "Default"))
            return MessageBuilder().newIdentity(True) 
        else:
            # else return false
            return MessageBuilder().newIdentity(False)