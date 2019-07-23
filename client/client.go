package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"strconv"
	"sync"
	"time"
)

type Parameters struct {
	name  string
	value int
}

func timeRequest(baseURL string, port string, command string, parameters Parameters) float64 {
	url := fmt.Sprintf("%s:%s/%s?%s=%d", baseURL, port, command, parameters.name, parameters.value)
	start := time.Now()
	response, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
		return -1
	}
	functionDuration := time.Since(start)
	responseBody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
		return -1
	}
	correct, expected := verifyResponse(command, responseBody, parameters.value)
	if correct {
		time := durationToMs(functionDuration)
		return time
	}
	fmt.Println("Incorrect return result. Output: " + string(responseBody) + ". Expected: " + expected)
	return -1
}

func verifyResponse(command string, response []byte, n int) (bool, string) {
	if command == "writedata" {
		expected := "done"
		return expected == string(response), expected
	}
	if command == "helloworld" {
		expected := "hello world"
		return expected == string(response), expected
	}
	if command == "calculatefib" {
		expected := fib(n)
		return string(response) == strconv.Itoa(expected), strconv.Itoa(expected)
	}
	return true, ""
}

func fib(n int) int {
	if n == 0 {
		return 0
	}
	if n == 1 {
		return 1
	}
	return fib(n-1) + fib(n-2)
}

func multipleConnections(baseURL string, connections int, port string, command string, parameters Parameters) float64 {
	var wg sync.WaitGroup
	var totalTime float64
	var countOperations int
	for i := 0; i < connections; i++ {
		wg.Add(1)
		go func(port string, command string, parameters Parameters, index int) {
			fmt.Println("started" + strconv.Itoa(index))
			time := timeRequest(baseURL, port, command, parameters)
			fmt.Println("finished" + strconv.Itoa(index))
			if time > 0 {
				totalTime += time
				countOperations++
			}
			wg.Done()
		}(port, command, parameters, i)
	}
	wg.Wait()
	if countOperations == 0 {
		return 0
	}
	return totalTime / float64(countOperations)
}

func durationToMs(functionDuration time.Duration) float64 {
	return math.Round(float64(functionDuration.Nanoseconds())) / float64(1e6)
}

func floatToString(float float64) string {
	return fmt.Sprintf("%f ms", float)
}

func strainAllEndpointns(connections int, baseURL string, command string, parameters Parameters) {
	fmt.Printf("\nCommand: %s. Connections: %d\n", command, connections)
	fmt.Println("Python:\t" + floatToString(multipleConnections(baseURL, connections, "5001", command, parameters)))
	fmt.Println("Go:\t" + floatToString(multipleConnections(baseURL, connections, "8080", command, parameters)))
	fmt.Println("Java:\t" + floatToString(multipleConnections(baseURL, connections, "9090", command, parameters)))
	fmt.Println("Node:\t" + floatToString(multipleConnections(baseURL, connections, "3000", command, parameters)))
	fmt.Println()
}

func main() {
	//url := "http://ec2-52-53-71-18.us-west-1.compute.amazonaws.com"
	url := "http://localhost"
	fmt.Println(floatToString(multipleConnections(url,
		10,
		"8080",
		"calculatefib",
		Parameters{"n", 3})))
}
