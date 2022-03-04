from models.userSession import UserSession

def test():
    us = UserSession("ray", "ba64077b-85b4-40f0-a5ac-480ad3e341b3","logout","xxxx")
    print(us.getUserName())
    print(us.getSessionID())
    print(us.getStatus())
    print(us.setPassword())