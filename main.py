#from testcases import test_threadpool, test_chatroominfo , test_configuration, test_localroominfo, test_remoteroominfo, test_fileReader
from flask import Flask, jsonify, request
from controllers.newIdentityProtocolHandler import newIdentityProtocolHandler

# creating a Flask app
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


# driver function
if __name__ == '__main__':
	app.run(debug = True)
