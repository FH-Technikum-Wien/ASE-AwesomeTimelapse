# ASE-AwesomeTimelapse
Small project using CI and CD Workflow

## REST API
### Docker Setup
In `AwesomeTimelapseREST`, run `docker-compose up --build -d`.

### Manual Setup
In `AwesomeTimelapseREST`, run:

```
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

The server is now available at http://127.0.0.1:8000. The web-UI is pretty self-explanatory and can be used for testing GET and POST requests. 
