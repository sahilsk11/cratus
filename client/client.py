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

'''
The client acts as the component receiving data from the back end

Think of this as the front end of the application requesting data from a service

Contains function to test each service
'''

ports = {"python": "5000",
         "java": "9090",
         "node": "3000",
         "go": "8080"
         }

lock = threading.Lock()

'''
Times a single request to an endpoint and returns the time

'''
def time_request(port, command, results=None, params=None):
    param_list = {}
    error = {"message": None, "error_object": None}
    failed = False
    traceback_message = None
    total_time = 0
    if params != None:
        for e in params:
            param_list[e[0]] = e[1]
    try:
        start_time = time.time()
        r = requests.get(
            "http://localhost:" + port + "/" + command,
            params=param_list,
            timeout=10000,
        )
        end_time = time.time()
        if not verify_response(command, r, params):
            error["message"] = "incorrect response"
            failed = True
        else:
            total_time = round((end_time - start_time) * 1000, 3)
    except Exception as e:
        error = {"message": "unhandled error in connection", "error_object": e}
        failed = True
        traceback_message = traceback.format_exc(limit=1)
    
    if results is None:
        return
    
    debug_report = {}
    successful_connection = error["error_object"] == None
    if successful_connection and failed:
        debug_report["response_text"] = r.text[:10]
    debug_report["successful_connection"] = successful_connection
    debug_report["error_message"] = error["message"]
    if (error["error_object"] != None):
        debug_report["unhandled_error"] = str(error["error_object"])
        debug_report["traceback"] = str(traceback_message)
    debug_report["port"] = port
    debug_report["status_code"]: r.status_code
    debug_report["execution_time"]: str(total_time)

    if results != None:
        lock.acquire()
        if not failed:
            results["result_times"].append(total_time)
        else:
            results["debug_report"] = debug_report
        lock.release()

def verify_response(command, r, n=20):
    if (command == "get-mini-employees"):
        return len(r.json()) == 10000
    if command == "calculatefib":
        expected = {20: "6765", 30: "832040", 34: "5702887"}
        return r.text == expected[n]
    return True

def parse_times(result_obj):
    result_times = result_obj["result_times"]
    if (len(result_times) == 0):
        result_obj["analysis"] = {"average_time": None, "min": None, "max": None, "stdev": None, "fail_percentage": 100}
        return
    min_time=min(result_times)
    max_time=max(result_times)
    average=round(sum(result_times) / len(result_times), 3)
    fail_percentage = round(
        result_obj["failed_connections"] / result_obj["attempted_connections"], 2) * 100
    if len(result_times) < 2:
        stdev=None
    else:
        stdev=statistics.stdev(result_times)
    result_obj["analysis"] = {"average_time": average, "min": min_time, "max": max_time, "stdev": stdev, "fail_percentage": fail_percentage}

def run_command_test(command, iterations, lang=None, print_result=False, save_data=False, plot_out=False, debug=False):
    if lang is None:
        out = {}
        out["final_analysis"] = {}
        for lang in ports.keys():
            out[lang] = run_command_test(command, iterations, lang, print_result=False, debug=debug)
            out["final_analysis"][lang] = out[lang]["analysis"]
        if print_result:
            pprint.pprint(out["final_analysis"])
        
        fh = datetime.datetime.now().strftime("%H-%M-%S")

        if save_data:
            json_to_csv(out, "sequential", command, iterations, fh)
        if plot_out:
            plot_result(out, "sequential", command, fh)
        return out
    
    # first run is usually slower so discard value
    time_request(ports[lang], "helloworld")
    result_data = {"result_times": []}
    for _ in range(0, iterations):
        time_request(ports[lang], command, result_data)
    result_data["failed_connections"] = iterations - \
        len(result_data["result_times"])
    result_data["attempted_connections"] = iterations
    parse_times(result_data)
    if debug:
        if result_data["analysis"]["fail_percentage"] == 0:
            print(lang, "services functioning normally")
        else:
            print("********************\n{} debug report".format(lang))
            pprint.pprint(result_data["debug_report"])
            print("********************\n")
    if print_result:
        print(result_data["analysis"])
    return result_data


def strain_server(lang, command, connections, out=None):
    threads = []
    results_dict = {"result_times": []}
    # first run is usually slower so discard value
    time_request(ports[lang], "helloworld")
    for i in range(0, connections):
        t = threading.Thread(target=time_request, args=(
            ports[lang], command, results_dict, [("i", i)]))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    results_dict["failed_connections"] = connections - \
        len(results_dict["result_times"])
    results_dict["attempted_connections"] = connections
    return results_dict

            
def run_strain_test(command, connections, lang=None, print_result=False, save_data=False, plot_out=False, debug=False):
    if lang is None:
        out = {}
        out["final_analysis"] = {}
        for lang in ports.keys():
            out[lang] = run_strain_test(command, connections, lang=lang, debug=debug, print_result=False)
            out["final_analysis"][lang] = out[lang]["analysis"]
        if print_result:
            pprint.pprint(out["final_analysis"])
            
        fh = datetime.datetime.now().strftime("%H-%M")
        if save_data or plot_out:
            os.mkdir("./datasets/" + fh)
            os.chdir("./datasets/" + fh)
        if save_data:
            json_to_csv(out, "multi-connection", command, connections, fh)
        if plot_out:
            plot_result(out, "multi-connection", command, fh)
        return out
            
    results = strain_server(lang, command, connections)
    parse_times(results)
    if debug:
        if results["analysis"]["fail_percentage"] == 0:
            print(lang, "services functioning normally")
        else:
            print("********************\n{} debug report".format(lang))
            pprint.pprint(results["debug_report"])
            print("********************\n")
    if print_result:
        print(results["analysis"]) 
    return results


def json_to_csv(json_obj, type, command, connections, out_file):
    filename = "data-" + out_file + ".csv"
    fh = open(filename, 'w')
    csv_writer = csv.writer(fh)
    csv_writer.writerow([command, type, connections])
    for key in json_obj.keys():
        if key is not 'final_analysis':
            csv_writer.writerow([key])
            for i in range(0, len(json_obj[key]["result_times"])):
                csv_writer.writerow([i, str(json_obj[key]["result_times"][i]*1000)])
            for stat in json_obj[key]["analysis"]:
                csv_writer.writerow([stat, json_obj[key]["analysis"][stat]])
            csv_writer.writerow("")
    fh.close()
    
def plot_result(json_obj, type, command, fh):
    for key in json_obj.keys():
        if key is not 'final_analysis':
            plt.bar(
                list(range(0, len(json_obj[key]["result_times"]))),
                json_obj[key]["result_times"],
                
            )
            filename = "{}-plot-{}".format(key, fh)
            plt.title("{} {} times ({})".format(key, command, type))
            plt.ylabel("times (ms)")
            plt.xlabel("iteration")
            plt.savefig(filename)
            plt.close()

#run_strain_test(connections=500, command="get-mini-employees", print_result=True, debug=True)

run_strain_test("get-mini-employee", 400, save_data=True, print_result=True, plot_out=True)
