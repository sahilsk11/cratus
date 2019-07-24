package main

import (
	"encoding/csv"
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

type Parameters struct {
	name  string
	value int
}

type Output struct {
	command     string
	connections int
	python      float64
	node        float64
	java        float64
	golang      float64
}

func timeRequest(baseURL string, port string, command string, parameters Parameters, index int) (float64, error) {
	url := fmt.Sprintf("%s:%s/%s?%s=%d", baseURL, port, command, parameters.name, parameters.value)
	start := time.Now()
	response, err := http.Get(url)
	functionDuration := time.Since(start)

	if err != nil {
		return -1, err
	}
	responseBody, err := ioutil.ReadAll(response.Body)
	if err != nil {
		return -1, err
	}
	correct, expected := verifyResponse(command, responseBody, parameters.value)
	if correct {
		time := durationToMs(functionDuration)
		return time, nil
	}
	return -1, errors.New("Incorrect return result. Output: " + string(responseBody) + ". Expected: " + expected)
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
	f, err := os.OpenFile("error.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal("Could not open log")
	}
	defer f.Close()
	//log.SetOutput(f)
	for i := 0; i < connections; i++ {
		wg.Add(1)
		go func(port string, command string, parameters Parameters, index int) {
			time, err := timeRequest(baseURL, port, command, parameters, index)
			if err == nil {
				totalTime += time
				countOperations++
			} else {
				fmt.Println(err)
			}
			wg.Done()
		}(port, command, parameters, i)
	}
	wg.Wait()
	if countOperations == 0 {
		return 0
	}
	failed := connections - countOperations
	fmt.Println("Failed: " + strconv.Itoa(failed))
	return totalTime / float64(countOperations)
}

func durationToMs(functionDuration time.Duration) float64 {
	return math.Round(float64(functionDuration.Nanoseconds())) / float64(1e6)
}

func floatToString(float float64) string {
	return fmt.Sprintf("%f", float)
}

func strainAllEndpoints(connections int, baseURL string, command string, parameters Parameters) Output {
	pythonTime := multipleConnections(baseURL, connections, "5001", command, parameters)
	goTime := multipleConnections(baseURL, connections, "8080", command, parameters)
	javaTime := multipleConnections(baseURL, connections, "9090", command, parameters)
	nodeTime := multipleConnections(baseURL, connections, "3000", command, parameters)
	output := Output{
		connections: connections,
		command:     command,
		python:      pythonTime,
		golang:      goTime,
		node:        nodeTime,
		java:        javaTime,
	}
	return output
}

func writeHeadingToCSV(output Output) {
	file, err := os.OpenFile("output.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()

	heading := []string{output.command}
	languages := []string{"", "python", "node", "java", "go"}

	writer.WriteAll([][]string{heading, languages})
}

func writeOutcomeToCSV(output Output) {
	file, err := os.OpenFile("output.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	writer := csv.NewWriter(file)
	defer writer.Flush()

	line := []string{
		strconv.Itoa(output.connections),
		floatToString(output.python),
		floatToString(output.node),
		floatToString(output.java),
		floatToString(output.golang),
	}
	writer.Write(line)
}

func main() {
	//url := "http://ec2-52-53-71-18.us-west-1.compute.amazonaws.com"
	url := "http://localhost"
	connections := 100
	command := "calcualtefib"
	parameters := Parameters{name: "n", value: 20}
	fmt.Println(floatToString(multipleConnections(url, connections, "8080", command, parameters)))
}
