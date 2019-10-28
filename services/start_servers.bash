node node/index.js > log.out &
go run go/endpoint.go > log.out &
source python/bin/activate
bash python/run_server.bash > log.out &
