class Message:
    def __init__(self, isFromClient, message):
        self._isFromClient = isFromClient
        self._message = message

    def isFromClient(self):
        return self._isFromClient

    def getMessage(self):
        return self._message