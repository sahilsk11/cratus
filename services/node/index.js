const express = require("express");
const { Pool } = require("pg");
const db_config = require("./db_config")

const app = express();
const pool = new Pool(db_config);

app.listen(3000, () => {
  console.log("Server running on port 3000");
});

app.get("/", (req, res) => {
  res.send("Node service is up and running");
});

app.get("/helloworld", (req, res) => {
  res.send("hello world");
});

app.get("/get-mini-employees", (request, response) => {
  pool.query('SELECT * FROM mini_employee', (err, res) => {
    if (err) console.log(err);
    response.json(res.rows);
  });
});

app.get("/readdata", (req, res, next) => {
  var fs = require("fs");
  var content = fs.readFileSync("../io/database.json");
  var jsonContent = JSON.parse(content);
  res.send(jsonContent);
});

app.get("/writedata", (req, res, next) => {
  var fs = require("fs");
  var content = fs.readFileSync("../io/database.json");
  var jsonContent = JSON.stringify(JSON.parse(content));
  fs.writeFile("../io/output.json", jsonContent, function (err) {
    if (err) {
      res.send("error");
    } else {
      res.send("done");
    }
  });
});

app.get("/calculatefib", (req, res, next) => {
  var n = req.query.n;
  if (n == undefined) {
    n = 20;
  }
  res.send(fib(n).toString());
});

function getMiniEmployees() {
  pool.query('SELECT * FROM mini_employee', (err, res) => {
    return res.rows;
  }
  );
}

function fib(n) {
  if (n == 0) {
    return 0;
  }
  if (n == 1) {
    return 1;
  }
  return fib(n - 2) + fib(n - 1);
}

app.get("/parsefile", (req, res, next) => {
  res.send(parseFile());
});

function parseFile(req, res, next) {
  var fs = require("fs");
  var content = fs.readFileSync("../io/MobyDick.txt");
  var dict = {}
  var parsedText = content.toString().match(/\b(\w+)\b/g);
  parsedText.forEach(function (word) {
    word = word.toLowerCase();
    if (!dict.hasOwnProperty(word)) {
      dict[word] = 1
    } else {
      dict[word]++;
    }
  });
  return dict;
}