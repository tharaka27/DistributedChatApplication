from models.remoteUserSession import RemoteUserSession

def test():
    rus = RemoteUserSession()
    rus.setUserName("ray")
    print(rus.getUserName())