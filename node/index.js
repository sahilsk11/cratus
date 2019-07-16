var express = require("express");
var app = express();
app.listen(3000, () => {
	console.log("Server running on port 3000");
});

app.get("/helloworld", (req, res, next) => {
	res.send("hello world");
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
	fs.writeFile("../io/output.json", jsonContent, function(err) {
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
	parsedText.forEach(function(word) {
		word = word.toLowerCase();
		if (!dict.hasOwnProperty(word)) {
			dict[word] = 1
		} else {
			dict[word]++;
		}
	});
	return dict;
}