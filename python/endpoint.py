import json
import flask
import re

app = flask.Flask(__name__)

@app.route('/helloworld')
def hello():
    return "hello world"

@app.route('/readdata')
def read_json():
    f = open("../io/database.json", "r")
    json_obj = json.load(f)
    return flask.jsonify(json_obj)

@app.route('/writedata')
def write_json():
    f = open("../io/database.json", "r")
    json_obj = json.load(f)

    o = open("../io/output.json", "w")
    json.dump(json_obj, o)
    return "done"

@app.route('/calculatefib')
def fib():
    try:
        n = int(flask.request.args.get("n"))
    except:
        n = 20
    return str(fib_helper(n))

def fib_helper(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib_helper(n - 1) + fib_helper(n - 2)

@app.route('/parsefile')
def parse_file():
    f = open("../io/MobyDick.txt", "r")
    raw_text = f.read()
    parsed_text = re.findall(r'\w+', raw_text)
    dict = {}
    for word in parsed_text:
        word = word.lower()
        if not word in dict:
            dict[word] = 1
        else:
            dict[word] += 1
    return json.dumps(dict)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
