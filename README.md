# cratus ⚡️
Measure execution speed of identical API endpoints developed in python, java, Golang, and Node.js.

### Background
There's much stigma around what the "best" backend language is. Python is notorious for being slow and unscalable. Most devs today refuse to touch anything that isn't node. Recently Golang is catching on. But how do they compare? Is one truly "faster" than the rest? How different are they?

Cratus aims to effectively answer these questions. While it is not possible to "benchmark" a language, per say, we can attempt to reduce incosistencies as much as possible and keep an eye out for major differences.

### Usage

Clone repo, run `build.sh` to set up dependencies. In the `client/` directory, `client.py` has functions for testing execution speed of services.

### Project Structure

- `frontend/` has an interactive demo to visualize how fast X milliseconds appears to a user
- `datasets/` has previous results including raw data and graphs from previous runs. All new runs are saved here as well.
- `client/` contains all files relating to measuring data
- `io/` contains some txt files for endpoints to parse
- `services/` contains all of actual endpoints, in their respective directories

### Setting up servers

#### Python
1. cd to `services/python`
2. Run `source env/bin/activate` to launch virtual env
3. To run directly from flask server, run `python endpoint.py`
4. To run from production gunicorn server, run `bash start_server.sh`
5. Run `deactivate` to exit virtual env

#### Node
1. cd to `services/node`
2. Run `npm start` to run directly from node application
3. Run `npm run prod` to run using pm2 (production process manager)

#### Golang
1. cd to `services/go`
2. Run `go run endpoint.go`

#### Java (requires IntelliJ)
1. Open the `spring/` directory in IntelliJ
2. Run `Endpoint.java` to run directly from application
3. Run `Server.java` to run using Tomcat production server