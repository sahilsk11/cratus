package main

import (
	"bufio"
	"database/sql"
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
	"time"

	"github.com/bdwilliams/go-jsonify/jsonify"
	_ "github.com/lib/pq"
)

const (
	host     = "localhost"
	port     = 5432
	user     = "postgres"
	password = "postgres"
	dbname   = "cratus-data"
)

func getMiniEmployees(db *sql.DB) string {
	sqlStatement := `SELECT * FROM mini_employee`
	rows, err := db.Query(sqlStatement)
	if err != nil {
		panic(err)
	}
	result := "[" + strings.Join(jsonify.Jsonify(rows), " ") + "]"
	return result
}

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

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Go endpoint is up and running")
	})
	http.HandleFunc("/helloworld", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "hello world")
	})
	http.HandleFunc("/get-mini-employees", func(w http.ResponseWriter, r *http.Request) {
		psqlInfo := fmt.Sprintf("host=%s port=%d user=%s "+
			"password=%s dbname=%s sslmode=disable",
			host, port, user, password, dbname)
		db, err := sql.Open("postgres", psqlInfo)
		if err != nil {
			panic(err)
		}
		err = db.Ping()
		if err != nil {
			panic(err)
		}
		start := time.Now()
		queryValues := r.URL.Query()
		param := queryValues.Get("i")
		fmt.Printf("Connection %s started\n", param)
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, getMiniEmployees(db))
		db.Close()
		fmt.Printf("Connection %s completed in %s\n", param, time.Since(start))
	})
	http.HandleFunc("/readdata", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, readJSON())
	})

	http.HandleFunc("/writedata", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, writeJSON())
	})

	http.HandleFunc("/calculatefib", func(w http.ResponseWriter, r *http.Request) {
		queryValues := r.URL.Query()
		param := queryValues.Get("n")
		n, err := strconv.Atoi(string(param))
		if err != nil {
			n = 20
		}
		fmt.Fprint(w, fib(n))
	})

	http.HandleFunc("/parsefile", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, parseFile())
	})

	log.Fatal(http.ListenAndServe(":8080", nil))
}
