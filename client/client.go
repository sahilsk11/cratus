package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"sync"
	"time"
)

type Parameters struct {
	name  string
	value string
}

func timeRequest(port string, command string, parameters Parameters) float64 {
	url := fmt.Sprintf("http://localhost:%s/%s", port, command)
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
	if verifyResponse(command, responseBody) {
		time := math.Round(float64(functionDuration.Nanoseconds())) / float64(1e6)
		return time
	}
	fmt.Println("Incorrect return result. Output: " + string(responseBody))
	return -1
}

func verifyResponse(command string, response []byte) bool {
	if command == "writedata" {
		return string(response) == "done"
	}
	if command == "helloworld" {
		return string(response) == "hello world"
	}
	return true
}

func multipleConnections(connections int, port string, command string, parameters Parameters) time.Duration {
	start := time.Now()
	var wg sync.WaitGroup

	for i := 0; i < connections; i++ {
		wg.Add(1)
		go func(port string, command string, parameters Parameters) {
			timeRequest(port, command, parameters)
			wg.Done()
		}(port, command, parameters)
	}
	wg.Wait()
	return time.Since(start)
}

func main() {
	fmt.Println(multipleConnections(100, "5001", "parsefile", Parameters{"none", "none"}))
	fmt.Println(multipleConnections(100, "8080", "parsefile", Parameters{"none", "none"}))
	fmt.Println(multipleConnections(100, "9090", "parsefile", Parameters{"none", "none"}))
	fmt.Println(multipleConnections(100, "3000", "parsefile", Parameters{"none", "none"}))
}
