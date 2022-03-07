import time
import threading
import random
#from testcases import test_threadpool, test_chatroominfo , test_configuration, test_localroominfo, test_remoteroominfo, test_fileReader
from flask import Flask, jsonify, request

# creating a Flask app
app = Flask(__name__)

# on the terminal type: curl http://127.0.0.1:5000/
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'POST'):
        json_data = request.json
        data = "hello world by post" + str(json_data)
        return jsonify({'data': data})


# driver function
if __name__ == '__main__':
	app.run(debug = True)


'''
def main():
    #test_threadpool.test()
    #test_chatroominfo.test()
    #test_configuration.test()
    #test_localroominfo.test()
    #test_remoteroominfo.test()
    test_fileReader.test()


if __name__ == "__main__":
    main()
'''