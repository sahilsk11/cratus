import requests
import time
import json
import threading
import csv
import statistics
import traceback
import datetime
import pprint

'''
The client acts as the component receiving data from the back end

Think of this as the front end of the application requesting data from a service

Contains function to test each service
'''

ports = {"python": "5001",
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
            total_time = end_time - start_time
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


def strain_server(lang, command, connections, out=None):
    threads = []
    results_dict = {"result_times":[]}
    # first run is usually slower so discard value
    time_request(ports[lang], "helloworld")
    for i in range(0, connections):
        t = threading.Thread(target=time_request, args=(ports[lang], command, results_dict, [("i", i)]))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    results_dict["failed_connections"] = connections - len(results_dict["result_times"])
    results_dict["attempted_connections"] = connections
    return results_dict


# Averages times in list
# Returns dict in format {average, min, max}
def parse_times(result_obj):
    result_times = result_obj["result_times"]
    if (len(result_times) == 0):
        result_obj["analysis"] = {"average_time": None, "min": None, "max": None, "stdev": None, "fail_percentage": 100}
        return
    min_time=s_to_ms(min(result_times))
    max_time=s_to_ms(max(result_times))
    average=s_to_ms(sum(result_times) / len(result_times))
    fail_percentage = round(
        result_obj["failed_connections"] / result_obj["attempted_connections"], 2) * 100
    if len(result_times) < 2:
        stdev=None
    else:
        stdev=statistics.stdev(result_times)
    result_obj["analysis"] = {"average_time": average, "min": min_time, "max": max_time, "stdev": stdev, "fail_percentage": fail_percentage}

def s_to_ms(s, places=3):
    return ("{:.3f}".format(round(s * 1000, places)))

'''
def run_lang_test(lang, command, iterations, debug=False, out=None):
    # first run is usually slower so discard value
    time_request(ports[lang], "helloworld")
    times=[]
    for i in range(0, iterations):
        (response_time, valid)=time_request(ports[lang], command)
        if valid:
            times.append(response_time)
        else:
            print("Invalid response on execution {} in {} for command {}".format(i, lang, command))
    if (out!=None):
        if lang not in out:
            out[lang] = {}
        out[lang]["times"] = times
    return parse_times(times, lang, out)
'''
def json_to_csv(json_obj, out_file=None):
    if out_file is None:
        out_file = "out-" + datetime.datetime.now().strftime("%H:%M") + ".csv"
    fh = open(out_file, 'w')
    csv_writer = csv.writer(fh)
    for key in json_obj.keys():
        csv_writer.writerow([key])
        for i in range(0, len(json_obj[key]["times"])):
            csv_writer.writerow([i, str(json_obj[key]["times"][i]*1000)])
        for stat in json_obj[key]["results"]:
            csv_writer.writerow([stat, json_obj[key]["results"][stat]])
        csv_writer.writerow("")
    fh.close()
            

def run_strain_test(connections, command, lang=None, print_result=False, debug=False):
    if lang is None:
        out = {}
        out["final_analysis"] = {}
        for lang in ports.keys():
            out[lang] = run_strain_test(connections, command, lang, debug=debug, print_result=False)
            out["final_analysis"][lang] = out[lang]["analysis"]
        if print_result:
            pprint.pprint(out["final_analysis"])
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
'''
def run_single_test(command, iterations, save_data=False):
    out_obj = None
    if (save_data):
        out_obj = {}
    print("Python:\t" + str(run_lang_test("python", command, iterations, out=out_obj, debug=True)))
    print("Go:\t" + str(run_lang_test("go", command, iterations, out=out_obj)))
    print("Node:\t" + str(run_lang_test("node", command, iterations, out=out_obj)))
    print("Java:\t" + str(run_lang_test("java", command, iterations, out=out_obj)))
    if save_data:
        json_to_csv(out_obj)
 '''   

run_strain_test(connections=500, command="get-mini-employees", print_result=True, lang="node", debug=True)
#run_single_test("get-mini_employees", 100, save_data=True)
