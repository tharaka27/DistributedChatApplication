class UserSession:
    def __init__(self, userName, sessionID, status, password ):
        self._userName = userName
        self._sessionID = sessionID        
        self._status = status
        self._password = password


    def getUserName(self):
        return self._userName
    def getSessionID(self):
        return self._sessionID
    def getStatus(self):
        return self._status
    def getPassword(self):
        return self._password

    def setUserName(self, userName):
        self._userName = userName
    def setSessionID(self, sessionID):
        self._sessionID = sessionID
    def setStatus(self, status):
        self._status = status
    def setPassword(self, password):
        self._password = password

    def __str__(self):
        return self._userName

    def __repr__(self):
        return self._userName