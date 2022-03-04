class UserSession:
    def __init__(self, managingServerID ):
        self._managingServerID = managingServerID

    def getUserName(self):
        return self._managingServerID

    def setUserName(self, managingServerID):
        self._managingServerID = managingServerID
