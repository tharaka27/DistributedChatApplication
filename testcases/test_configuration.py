from models.configuration import ServerConfiguration

def test():
    s = ServerConfiguration("s1", "localhost", 4444, 5555)
    print(s.getServerName())
    print(s.getAddress())
    print(s.getClientPort())
    print(s.getCoordinationPort())

    s.setServerName("s_1")
    s.setAddress("192.8.91.2")
    s.setClientPort(4004)
    s.setCoordinationPort(5005)
    print(s.getServerName())
    print(s.getAddress())
    print(s.getClientPort())
    print(s.getCoordinationPort())