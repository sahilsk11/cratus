import requests
import time
import json
import threading
import csv

ports = {
    "python": "5001",
    "java": "9090",
    "node": "3000",
    "go": "8080",
}

commands = ["helloworld", "writedata", "readdata", "parsefile", "calculatefib"]

lock = threading.Lock()

def time_request(port, command, results=None, params=None):
    start_time = time.time()
    try:
        r = requests.get("http://localhost:" + port + "/" + command, params=params)
        end_time = time.time()
        if not verify_response(command, r):
            print("error")
            return "error. incorrect result"
    except Exception as e:
        print(e)
        return "error: " + str(e)
    total_time = end_time - start_time
    if results is None:
        return total_time
    lock.acquire()
    results.append(total_time)
    lock.release()


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
        f = open("../io/database.json", "r")
        content = json.load(f)
        response_json = r.json()
        f.close()
        return len(content) == len(response_json)
    if command == "parsefile":
        response_json = r.json()
        return "moby" in response_json
    return True


def strain_server(port, command, connections):
    threads = []
    results = []
    for i in range(0, connections):
        t = threading.Thread(target=time_request, args=(port, command, results))
        threads.append((t, i))
        t.start()
    for t in threads:
        t[0].join()
    if (len(results) != connections):
        print("Error in calculating results. Port: " + port)
        return "error"

    avg = sum(results) / connections
    return avg

def strain_all_servers(command, connections):
    results = {}
    for key in ports:
        results[key] = strain_server(ports[key], command, connections)
    return results


def writeToCSV(results, command, connections, header=False, mode="a"):
    f = open(command+".csv", mode)
    writer = csv.writer(f)

    if header:
        writer.writerow([command, "python", "java", "node", "go"])
    writer.writerow([connections, results["python"], results["java"], results["node"], results["go"]])
    f.close()

def conduct_test(command):
    for i in range(0, 1001, 100):
        if i == 0:
            i = 1
        results = strain_all_servers(command, i)
        if i == 1:
            header = True
            mode = "w"
        else:
            header = False
            mode = "a"
        writeToCSV(results, command, i, header, mode)


# run one random request because the first call is always slower
time_request("5001", "helloworld")

conduct_test("readdata")

