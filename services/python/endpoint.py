import json
import flask
import re
import psycopg2
import passwords
import timeit

app = flask.Flask(__name__)

connection = psycopg2.connect(user="postgres", password=passwords.postgres_password(), host="localhost", port="5432", database="cratus-data")

@app.route('/')
def healthcheck():
    return "python service is up and running"

@app.route('/helloworld')
def hello():
    return "hello world"

@app.route('/get-mini-employees')
def get_mini_employee_data():
  cursor = connection.cursor()
  postgres_get_query = """SELECT * FROM mini_employee"""
  cursor.execute(postgres_get_query)
  #print("Time elapsed: " + str((timeit.default_timer() - start) * 1000) + " ms")
  out = flask.jsonify(cursor.fetchall())
  #print("Additional time: " + str((timeit.default_timer() - start) * 1000) + " ms")
  #print("completed task")
  return out


@app.route('/calculatefib')
def fib():
    try:
        n = int(flask.request.args.get("n"))
    except:
        return "Error: missing parameter"
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
    return flask.jsonify(dict)


if __name__ == "__main__":
    app.run(debug=False, threaded=False)
