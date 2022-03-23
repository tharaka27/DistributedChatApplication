import json

# IMPORTANT !!!
#
# For server to server communication use -> json.dumps
# For server to client communication use -> jsonify
# This is due to flask maintaining a context when using jsonify
# using this context for server to server communication raises
# out of context exception

class MessageBuilder:
    _instance = None

    def __init__(self):
        if MessageBuilder._instance != None:
            raise Exception("This is a singleton class") 
        else:
            MessageBuilder._instance = self

    @staticmethod
    def getInstance():
        if MessageBuilder._instance == None :
            MessageBuilder()
        return MessageBuilder._instance

    def newIdentity(self, approve):
        message = {}
        message["type"] = "newidentity"
        message["approved"] = str(approve)
        return json.dumps(message)
    
    def newChatRoom(self, roomId, approve):
        message = {}
        message["type"] = "createroom"
        message["roomid"] = roomId
        message["approved"] = str(approve)
        return json.dumps(message)

    def coordinatorNotAlive(self, protocol):
        print("[Error] Coordinator not alive" + protocol + " cannot execute")
        return json.dumps({"error" : "Coordinator not alive"}) + "\n"

    def createNewIdentity(self, approve):
        message = {}
        if approve:
            message = { "type" : "create_identity_done" ,"approved": "True"}
        else:
            message = { "type" : "create_identity_done" ,"approved": "False"}
        return json.dumps(message)
    
    def createNewChatRoom(self, approve):
        message = {}
        if approve:
            message = { "type" : "create_chatroom_done" ,"approved": "True"}
        else:
            message = { "type" : "create_chatroom_done" ,"approved": "False"}
        return json.dumps(message)

    def distributeNewIdentity(self, name):
        message = { "type" : "create_identity" ,"identity": name }
        return json.dumps(message)

    def errorServer(self):
        message = { "type" : "error message" }
        return json.dumps(message)
    
    def roomChange(self,identity,former,new):
        message = {}
        message["type"] = "roomchange"
        message["identity"] = identity
        message["former"] = former
        message["roomid"] = new
        return json.dumps(message)
    
    def route(self,room,host,port):
        message = {}
        message["type"] = "route"
        message["roomid"] = room
        message["host"] = str(host)
        message["port"] = str(port)
        return json.dumps(message)  

    