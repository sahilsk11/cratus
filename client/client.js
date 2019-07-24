const request = require("request");
const util = require("util")

function timeRequest(url, port, command, n) {
    url = util.format("%s:%s/%s", url, port, command)
    if (n != null) {
        url += "?n=" + n;
    }
    var start = new Date();
    var end;
    request(url, (err, res, body) => {
        end = new Date() - start;
        if (verifyResponse(body)) {
            return end;
        }
    });
}

function verifyResponse(command, body) {
    return true;
}

url = "http://localhost"
port = 8080
command = "helloworld"
n = 10

timeRequest(url, port, command, n)