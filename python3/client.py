import requests
import time

ports = {
    "python": "5000",
    "spring": "8081"
}

def test_endpoints(command):
    print("Testing " + command + ":")
    python_time = time_request("python", command)
    spring_time = time_request("spring", command)
    print("Python: " + str(python_time) + "\nSpring: " + str(spring_time) + "\n")

def time_request(lang, command):
    start_time = time.time()
    r = requests.get("http://localhost:" + ports[lang] + "/" + command)
    print(r.text)
    if (r.text == ""):
        return "error"
    end_time = time.time()
    return end_time - start_time


test_endpoints("helloworld")
test_endpoints("readdata")
test_endpoints("writedata")