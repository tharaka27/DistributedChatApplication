from flask import jsonify

class MessageBuilder:

    def newIdentity(self, approve):
        message = {}
        message["type"] = "newidentity"
        message["approved"] = str(approve)
        return jsonify(message)

    