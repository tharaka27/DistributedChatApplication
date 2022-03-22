from flask import jsonify

class MessageBuilder:
    _instance = None

    def __init__(self):
        if MessageBuilder._instance != None:
            raise Exception("This is a singleton class") 
        else:
            MessageBuilder._instance = self

    @staticmethod
    def getInstance():
        if _instance != None :
            return _instance
        else :
            MessageBuilder()

    def newIdentity(self, approve):
        message = {}
        message["type"] = "newidentity"
        message["approved"] = str(approve)
        return jsonify(message)

    def coordinatorNotAlive(self, protocol):
        print("[Error] Coordinator not alive" + protocol + " cannot execute")
        return jsonify({"error" : "Coordinator not alive"})

    