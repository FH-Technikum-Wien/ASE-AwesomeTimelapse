# ASE-AwesomeTimelapse
Small project using CI and CD Workflow

## REST API
### Docker Setup
In `AwesomeTimelapseREST`, run `docker-compose up --build -d`.

Get the IP of that server: `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' django`

## Communication

![](communication_graph.png)
