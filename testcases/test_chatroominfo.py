from models.chatroominfo import ChatRoomInfo

def test():
    s = ChatRoomInfo()
    s.setChatRoomID("chatroom1")
    print(s.getChatRoomId())