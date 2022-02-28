from models.remoteroominfo import RemoteRoomInfo

def test():
    remote = RemoteRoomInfo()
    remote.setChatRoomID("chatroom1")
    remote.setCoordinator("255.255.25.3")
    print(remote.getChatRoomId())
    print(remote.getCoordinator())