from models.chatroominfo import ChatRoomInfo

class RemoteRoomInfo(ChatRoomInfo):

    def __init__(self, coordinator=""):
        self.coordinator = coordinator

    def setCoordinator(self, coordinator):
        self.coordinator = coordinator

    def getCoordinator(self):
        return self.coordinator
