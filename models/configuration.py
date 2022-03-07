from .constants import LOCAL_HOST_ADDRESS

class ServerConfiguration:
    def __init__(self, server_name, address, clients_port, coordination_port):
        self._server_name   = server_name
        self._address       = self.resolveServerAddress(address)
        self._client_port   = clients_port
        self._coordination_port = coordination_port

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

    def resolveServerAddress(self, server_address):
        if server_address == "localhost":
            return LOCAL_HOST_ADDRESS
        else:
            return server_address