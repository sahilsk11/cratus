import requests
import time
import json
import threading
import csv
import statistics
import traceback
import datetime
import pprint
import matplotlib.pyplot as plt
import os
import random

'''
The client acts as the component receiving data from the back end

Think of this as the front end of the application requesting data from a service

Contains function to test each service
'''

ports = {
    "python": "8000",
    "node": "8080",
    #"go": "8080"
}

lock = threading.Lock()

'''
Times a single request to an endpoint and returns the time

port: the port to request
command: the endpoint to request
results: stores the output as a dict in results
params: list of URL parameters as tuples
'''
def time_single_request(port, command, hostname):
    try:
        start_time = time.time()
        r = requests.get("http://{}:{}/{}".format(hostname, port, command))
        end_time = time.time()   
        return (round((end_time - start_time) * 1000, 3), r, None)
    except Exception as _:
        traceback_message = traceback.format_exc(limit=1)
        error = {"message": "unhandled error in connection", "error_object": traceback_message}
        return (None, None, error)

def verify_response(command, r):
    if (r.status_code != 200):
        return False
    if (command == "get-mini-employees"):
        return len(r.json()) == 10000
    if command == "calculatefib":
        return r.text == "6765"
    if command == "helloworld":
        return r.text == "hello world"
    if command == "portfolio":
        return len(r.json().keys()) == 5
    print("Warning: unknown command")
    return True

def complete_request(lang, command, results=None, host="localhost"):
    (time, response, error) = time_single_request(ports[lang], command, host)
    if time != None:
        if verify_response(command, response):
            if results != None:
                lock.acquire()
                results["result_times"].append(time)
                lock.release()
            return (time, None)
        else:
            error = {"message": "invalid response", "response_text": response.text}
            if results != None:
                lock.acquire()
                results["error_count"] += 1
                results["errors"].append(error)
                lock.release()
            return (None, error)
    else:
        if results != None:
            lock.acquire()
            results["error_count"] += 1
            results["errors"].append(error)
            lock.release()
        return (None, error)
        

def analyze_result_times(result_obj, attempted_connections, store_errors=False):
    result_times = result_obj["result_times"]
    if (len(result_times) == 0):
        return {
            "average_time": None,
            "min": None,
            "max": None,
            "stdev": None,
            "error_count": result_obj["error_count"],
            "fail_percentage": 100,
            "errors": result_obj["errors"] if store_errors else []
        }
    min_time=min(result_times)
    max_time=max(result_times)
    average=round(sum(result_times) / len(result_times), 3)
    fail_percentage = round(result_obj["error_count"] * 100 / attempted_connections, 2)
    if len(result_times) < 2:
        stdev=None
    else:
        stdev=statistics.stdev(result_times)
    return {
        "average_time": average,
        "min": min_time,
        "max": max_time,
        "stdev": stdev,
        "fail_percentage": fail_percentage,
        "error_count": result_obj["error_count"],
        "attempted_connections": attempted_connections, 
        "errors": result_obj["errors"] if store_errors else []
    }

'''
Runs a sequential command test.

command: the endpoint to request
iterations: the number of requests to record (more data points)
lang: the language to test. If none is provided, test all.
print_results: flag to print the analysis of the test
save_data: flag to save the run data to CSV
plot_out: flag to save the graph of the data
debug: flag to show more verbose test information
'''
def run_sequential_test(lang, command, iterations, plot=False):
    result_data = {"result_times": [], "error_count": 0, "errors": []}
    for _ in range(0, iterations):
        complete_request(lang, command, results=result_data)
    analysis = analyze_result_times(result_data, iterations)
    if (plot):
        plot_result(lang, command, result_data)
    return analysis

'''
Generates multiple threads to simulate simultaneous connections

lang: the language to test
command: the endpoint to request
connections: the number of threads to generate
'''
def strain_server(lang, command, connections, plot=False):
    threads = []
    result_data = {"result_times": [], "error_count": 0, "errors": []}
    for _ in range(0, connections):
        t = threading.Thread(target=complete_request, args=(
            lang, command, result_data))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    analysis = analyze_result_times(result_data, connections)
    if plot:
        plot_result(lang, command, result_data)
    return analysis


def json_to_csv(json_obj, type, command, connections, lang=None):
    filename = "data.csv"
    fh = open(filename, 'w')
    csv_writer = csv.writer(fh)
    csv_writer.writerow([command, type, connections])
    if lang is not None:
        csv_writer.writerow([lang])
        for i in range(0, len(json_obj["result_times"])):
            csv_writer.writerow([i, str(json_obj["result_times"][i])])
        for stat in json_obj["analysis"]:
            csv_writer.writerow([stat, json_obj["analysis"][stat]])
        csv_writer.writerow("")
    else:
        for key in json_obj.keys():
            if key is not 'final_analysis':
                csv_writer.writerow([key])
                for i in range(0, len(json_obj[key]["result_times"])):
                    csv_writer.writerow([i, str(json_obj[key]["result_times"][i])])
                for stat in json_obj[key]["analysis"]:
                    csv_writer.writerow([stat, json_obj[key]["analysis"][stat]])
                csv_writer.writerow("")
    fh.close()
    
def plot_result(lang, command, results_data):
        plt.bar(
            list(range(0, len(results_data["result_times"]))),
            results_data["result_times"],
        )
        filename = "{}-plot".format(lang)
        plt.title("{} {} times".format(lang, command))
        plt.ylabel("response time (ms)")
        plt.xlabel("iteration")
        plt.savefig(filename)
        plt.close()

if __name__ == "__main__":
    #print(strain_server("python", "portfolio", 20, plot=True))
    print(strain_server("node", "portfolio", 20, plot=True))
