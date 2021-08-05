# Upsource mock service

The Mock Service is for testing Upsource Integration. The Mock Service uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework.

1. Install Python libraries:
   - [Flask](https://flask.palletsprojects.com/en/1.1.x/) (pip3 install Flask)
   - [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) (pip3 install Flask-HTTPAuth)

(make sure that `flask` command is available in `PATH`)

2. Specify the path to the Flask app: `export FLASK_APP=mock/mock_service.py`

3. Run Flask app: `flask run`


## Script mode to install as daemon (service)

Run: `sudo daemon/install_as_daemon.sh <integration path> [http port]`

where:
- `<integration path>` is `/opt/site.onevizion.com_integration-scheduler/<integration ID>`
- `[http port]` is optional HTTP port number to use in service (`8085` by default)
