from flask import Flask, jsonify, request
import json
from flask_basicauth import BasicAuth
import random

app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'hello'
app.config['BASIC_AUTH_PASSWORD'] = '123'

basic_auth = BasicAuth(app)


@app.route('/redfish/v1/Systems/1')
@basic_auth.required
def system():
    with open('system.json') as f:
        temp = json.load(f)
    return jsonify(temp)


@app.route('/sunlf', methods=['POST'])
@basic_auth.required
def sunlf():
    print(request.headers)
    print(request.json)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


class Data():
    def __init__(self, humid, temp):
        self.humid = humid
        self.temp = temp


@app.route('/getdata', methods=['GET'])
def getData():
    data = Data(random.randint(1, 10), random.randint(10, 20))
    return json.dumps(data.__dict__), 200, {'ContentType': 'application/json'}


@app.route('/postdata/<device_id>', methods=['POST'])
def postData(device_id):   
    device_name = request.headers['device_name'] # get header
    print("get request, json data is {},device_id is {},device name is {}".format(
        request.json, device_id,device_name))
    return json.dumps({'result': "succeed"}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
