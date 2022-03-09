from .constants import LOCAL_HOST_ADDRESS, RANDOM_RANGE
from random import randrange

class ServerConfiguration:
    def __init__(self, server_name, address, clients_port, coordination_port, heart_port, i_id):
        self._server_name   = server_name
        self._address       = self.resolveServerAddress(address)
        self._client_port   = clients_port
        self._coordination_port = coordination_port
        self._id = i_id #randrange(RANDOM_RANGE)
        self._heart_port = heart_port

    def getServerName(self):
        return self._server_name
    
    def setServerName(self, server_name):
        self._server_name = server_name
    
    def getAddress(self):
        return self._address
    
    def setAddress(self, address):
        self._address = address
    
    def getClientPort(self):
        return self._client_port 
    
    def setClientPort(self, clients_port):
        self._client_port = clients_port
    
    def getCoordinationPort(self):
        return self._coordination_port

    def setCoordinationPort(self, coordination_port):
        return self._coordination_port

    def setHeartPort(self, heart_port):
        self._heart_port = heart_port
    
    def getHeartPort(self):
        return self._heart_port

    def setID(self, i_id):
        self._id = i_id

    def getId(self):
        return self._id

    def resolveServerAddress(self, server_address):
        if server_address == "localhost":
            return LOCAL_HOST_ADDRESS
        else:
            return server_address


    def __repr__(self):
        return "name: " + self._server_name + " address:" + self._address \
            + " client port:" + self._client_port + " coordiantion port:" + \
                self._coordination_port + " id " + str(self._id)