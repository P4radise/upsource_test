# Upsource mock service

The Mock Service is for testing Upsource Integration. The Mock Service uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework.

1. Install Python libraries (global):
   - [Flask](https://flask.palletsprojects.com/en/1.1.x/) (pip install Flask)
   - [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) (pip install Flask-HTTPAuth)

(make sure that `flask` command is available in `PATH`)

2. Specify the path to the Flask app: `export FLASK_APP=mock/mock_service.py`

3. Run Flask app: `flask run`


## Script mode to install as service (run from integration user)

```
pip install Flask
pip install Flask-HTTPAuth

which flask || echo No flask in PATH!

export SERVICE_NAME=upsource_sync_mock
export SERVICE_PORT=8085
export SERVICE_UN=$(whoami)
export SERVICE_PATH=$(pwd)
export SERVICE_ENV_FILENAME=service_env.conf

(< service_env.template envsubst | tee "$SERVICE_ENV_FILENAME") >/dev/null
(< service_systemd.template envsubst | tee "/usr/lib/systemd/system/${SERVICE_NAME}.service") >/dev/null
systemctl enable "$SERVICE_NAME" && systemctl start "$SERVICE_NAME"
```