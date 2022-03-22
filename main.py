#from testcases import test_threadpool, test_chatroominfo , test_configuration, test_localroominfo, test_remoteroominfo, test_fileReader
from flask import Flask, jsonify, request
from controllers.newIdentityProtocolHandler import newIdentityProtocolHandler
from models import serverstate
from utilities.fileReader import FileReader
from algorithms.bully import Bully
from controllers.JSONMessageBuilder import MessageBuilder 
import os
app = Flask(__name__)

# on the terminal type: curl http://127.0.0.1:5000/
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'POST'):
        json_data = request.json
        msg_type = json_data["type"]
        if(msg_type == "newidentity"):
            return newIdentityProtocolHandler(json_data).handle()

        elif(msg_type == "roomchange"):
            pass

        else:
            return jsonify({ "data" : "wrong protocol.please check again" })

@app.before_first_request
def Initialization():
    LOCAL_SERVER_NAME = os.environ.get('s')
    
    f = FileReader()
    config_objects = f.populate("configuration.txt")
    for i in config_objects:

        print("Setting ->" + i.getServerName() + i.getAddress() + ":" + str(i.getHeartPort()))
        if i.getServerName() == LOCAL_SERVER_NAME:
            serverstate.LOCAL_SERVER_CONFIGURATION = i
            #LOCAL_SERVER_CONFIGURATION = i
        else:
            serverstate.REMOTE_SERVER_CONFIGURATIONS.append(i)
            #REMOTE_SERVER_CONFIGURATIONS.append(i)


    print("[INFO] Initializing server with.....")   
    print("[INFO] Local server configuration")
    print( serverstate.LOCAL_SERVER_CONFIGURATION )
    print("[INFO] Remote server configurations")
    print( serverstate.REMOTE_SERVER_CONFIGURATIONS)

    bully  = Bully()
    bully.run()
    
    msg = MessageBuilder.getInstance()


# driver function
if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('port')))
