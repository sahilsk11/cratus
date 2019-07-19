import requests
import time
import json
import threading
import queue

ports = {
    "python": "5001",
    "java": "9090",
    "node": "3000",
    "go": "8080",
}

commands = ["helloworld", "writedata", "readdata", "parsefile", "calculatefib"]


def time_request(port, command, params=None):
    start_time = time.time()
    try:
        r = requests.get("http://localhost:" + port + "/" + command, params=params)
        end_time = time.time()
        if not verify_response(command, r):
            return "error. incorrect result"
    except Exception as e:
        return "error: " + str(e)
    print(end_time - start_time)
    return end_time - start_time


def test_all_endpoints(command, params=None):
    spring_time = time_request(ports["java"], command, params)
    python_time = time_request(ports["python"], command, params)
    node_time = time_request(ports["node"], command, params)
    go_time = time_request(ports["go"], command, params)
    return {
        "command": command,
        "spring_time": spring_time,
        "python_time": python_time,
        "node_time": node_time,
        "go_time": go_time
    }


def print_results(times):
    print("Testing " + times["command"] + ":")
    print("Python:\t" + str(times["python_time"]) +
        "\nSpring:\t" + str(times["spring_time"]) +
        "\nNode:\t" +str(times["node_time"]) +
        "\nGo:\t\t" + str(times["go_time"]) + "\n")


def verify_response(command, r):
    if command == "writedata":
        return r.text == "done"
    if command == "helloworld":
        return r.text == "hello world"
    if command == "readdata":
        f = open("io/database.json", "r")
        content = json.load(f)
        response_json = r.json()
        return len(content) == len(response_json)
    if command == "parsefile":
        response_json = r.json()
        return "moby" in response_json
    return True


def destroy_server(port, command, connections):
    threads = []
    for i in range(0, connections):
        t = threading.Thread(target=time_request, args=(port, command))
        threads.append((t, i))
        t.start()
    for t in threads:
        t[0].join()


# run one random request because the first call is always slower
time_request("5001", "helloworld")
time_request("5001", "helloworld")
time_request("5001", "helloworld")
time_request("5001", "helloworld")
time_request("5001", "helloworld")


#destroy_server("5001", "helloworld", 10)
