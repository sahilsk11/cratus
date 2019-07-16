import requests
import time
import json
import csv

ports = {
    "python": "5000",
    "java": "8081",
    "node": "3000",
    "go": "8080"
}

times = {
	"python": {},
	"java": {},
	"node": {},
	"go": {}
}

def test_endpoints(command, params=None, test=False, printInfo=True):
    spring_time = time_request("spring", command, params)
    python_time = time_request("python", command, params)
    node_time = time_request("node", command, params)
    go_time = time_request("go", command, params)
    if not test:
    	times["python"][command] = python_time
    	times["java"][command] = spring_time
    	times["node"][command] = node_time
    	times["go"][command] = go_time
    if (printInfo and not test):
        print("Testing " + command + ":")
        print("Python:\t" + str(python_time) + 
   	 	"\nSpring:\t" + str(spring_time) + 
    	"\nNode:\t" +str(node_time) + 
    	"\nGo:\t\t" + str(go_time) + "\n")

def time_request(lang, command, params=None):
    start_time = time.time()
    try:
    	r = requests.get("http://localhost:" + ports[lang] + "/" + command, params=params)
    	if not verify_response(command, r):
    		return "error. incorrect result"
    except:
    	return "error"
    end_time = time.time()
    return end_time - start_time
    
def verify_response(command, r):
	if (command == "writedata"):
		return r.text == "done"
	if (command == "helloworld"):
		return r.text == "hello world"
	if (command == "readdata"):
		f = open("io/database.json", "r")
		content = json.load(f)
		response_json = r.json()
		return len(content) == len(response_json)
	if (command == "parsefile"):
		response_json = r.json()
		return "moby" in response_json
	return True
	
def print_totals():
	print("Total time:")
	for key in times.keys():
		total = 0
		for command in times[key].keys():
			total = times[key][command]
		if (key == "go"):
			key = "go\t"
		print(key + ":\t\t" + str(total))
		
def load_server(lang, connections, command, params=None):
	total = 0
	for i in range(0, connections):
		addition = time_request(lang, command, params)
		if addition == "error":
			return addition
		total += addition
	return total


test_endpoints("helloworld", test=True)

#print_totals()

def track_all():
	results = {
		
	}
	commands = ["helloworld", "readdata", "writedata", "calculatefib"]
	languages = ["python", "java", "node", "go"]
	connectionsMax = 100
	for command in commands:
		for i in range(0, connectionsMax, 10):
			for lang in languages:
				if i == 0:
					i += 1
				if command not in results:
					results[command] = {}
				if i not in results[command]:
					results[command][i] = {}
				results[command][i][lang] = load_server(lang, i, command) / i
	print(results)
	return results
	
def save_as_csv():
	f = open("data.csv", "w")
	writer = csv.writer(f)
	data = track_all()
	for command in data:
		writer.writerow([command, "python", "java", "node", "go"])
		for i in data[command]:
			row_data = data[command][i]
			writer.writerow([i, row_data["python"], row_data["java"], row_data["node"], row_data["go"]])
			
save_as_csv()
	
	
