package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
)

func readJSON() string {
	fileHandle, err := os.Open("../io/database.json")
	if err != nil {
		log.Fatal(err)
	}
	defer fileHandle.Close()
	rawInput, err := ioutil.ReadAll(fileHandle)
	if err != nil {
		log.Fatal(err)
	}

	var decodedFile interface{}
	json.Unmarshal(rawInput, &decodedFile)
	output, err := json.Marshal(decodedFile)
	if err != nil {
		log.Fatal(err)
	}

	return string(output)
}

func writeJSON() string {
	fileHandle, err := os.Open("../io/database.json")
	if err != nil {
		log.Fatal(err)
	}
	defer fileHandle.Close()

	rawInput, err := ioutil.ReadAll(fileHandle)
	if err != nil {
		log.Fatal(err)
	}

	var decodedFile interface{}
	json.Unmarshal(rawInput, &decodedFile)
	output, err := json.Marshal(decodedFile)

	outFile, err := os.Create("../io/output.json")
	defer outFile.Close()
	if err != nil {
		log.Fatal(err)
	}
	_, err = io.WriteString(outFile, string(output))
	if err != nil {
		log.Fatal(err)
	}
	return "done"
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

func parseFile() string {
	fileHandle, err := os.Open("../io/MobyDick.txt")
	defer fileHandle.Close()
	if err != nil {
		log.Fatal(err)
	}

	dict := make(map[string]int)
	scan := bufio.NewScanner(fileHandle)
	regExp, _ := regexp.Compile("[a-zA-Z]+")
	for scan.Scan() {
		line := scan.Text()
		cleanedLine := regExp.FindAllString(line, -1)
		for _, word := range cleanedLine {
			word = strings.ToLower(word)

			//checks if the word is in dict
			if _, ok := dict[word]; ok {
				dict[word]++
			} else {
				dict[word] = 1
			}
		}
	}
	output, err := json.Marshal(dict)
	return string(output)
}

func main() {
	http.HandleFunc("/helloworld", func(w http.ResponseWriter, r *http.Request) {
		fmt.Println("/helloworld")
		fmt.Fprintf(w, "hello world")
	})

	http.HandleFunc("/readdata", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, readJSON())
		fmt.Println("/readdata")
	})

	http.HandleFunc("/writedata", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, writeJSON())
		fmt.Println("/writedata")
	})

	http.HandleFunc("/calculatefib", func(w http.ResponseWriter, r *http.Request) {
		queryValues := r.URL.Query()
		param := queryValues.Get("n")
		n, err := strconv.Atoi(string(param))
		if err != nil {
			n = 20
		}
		fmt.Fprint(w, fib(n))
		fmt.Println("/calculatefib")
	})

	http.HandleFunc("/parsefile", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, parseFile())
		fmt.Println("/parsefile")
	})

	log.Fatal(http.ListenAndServe(":8080", nil))
}
