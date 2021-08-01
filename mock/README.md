# Upsource mock service

The Mock Service is for testing Upsource Integration. The Mock Service uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework.

1. Install Python libraries:
   - [Flask](https://flask.palletsprojects.com/en/1.1.x/) (pip3 install Flask)
   - [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) (pip3 install Flask-HTTPAuth)

(make sure that `flask` command is available in `PATH`)

2. Specify the path to the Flask app: `export FLASK_APP=mock/mock_service.py`

3. Run Flask app: `flask run`


## Script mode to install as service (run from `root` user and `mock` directory)

```
pip3 install Flask
pip3 install Flask-HTTPAuth

export SERVICE_NAME=upsource_sync_mock
export SERVICE_PORT=8085
export SERVICE_UN=u_[paste Integration ID here]
export SERVICE_PATH=$(pwd)
export SERVICE_ENV_FILENAME=service_env.conf

(< service_env.template envsubst | tee "$SERVICE_ENV_FILENAME") >/dev/null
chown $SERVICE_UN $SERVICE_ENV_FILENAME

(< service_systemd.template envsubst | tee "/usr/lib/systemd/system/${SERVICE_NAME}.service") >/dev/null

systemctl enable "$SERVICE_NAME" && systemctl start "$SERVICE_NAME"
systemctl status "$SERVICE_NAME"
```