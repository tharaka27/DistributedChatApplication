from JSONMessageBuilder import MessageBuilder

class routeProtocolHandler:
    def __init__(self, json_data):
        self._protocol = "route"
        self._name = json_data["identity"]
        
    def handle(self):
        # check for the availability of name

        if self._name == "Tharaka":
            # if success return true
            return MessageBuilder().newIdentity(True) 
        else:
            # else return false
            return MessageBuilder().newIdentity(False)