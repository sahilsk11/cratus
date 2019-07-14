import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/helloworld')
def hello():
    return "hello world"

@app.route('/readdata')
def read_json():
    f = open("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/database.json", "r")
    json_obj = json.load(f)
    return str(json_obj)

@app.route('/writedata')
def write_json():
    f = open("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/database.json", "r")
    json_obj = json.load(f)

    o = open("/Users/sahil/OneDrive - purdue.edu/Portfolio/endpointspeed/output.json", "w")
    json.dump(json_obj, o)
    return "done"

if __name__ == "__main__":
    app.run(debug=True)