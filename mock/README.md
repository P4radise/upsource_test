# Upsource mock service

The Mock Service is for testing Upsource Integration. The Mock Service uses [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework.

1. Install Python libraries (global):
   - [Flask](https://flask.palletsprojects.com/en/1.1.x/) (pip install Flask)
   - [Flask-HTTPAuth](https://flask-httpauth.readthedocs.io/en/latest/) (pip install Flask-HTTPAuth)

(make sure that `flask` command is available in `PATH`)

2. Specify the path to the Flask app: `export FLASK_APP=mock/mock_service.py`

3. Run Flask app: `flask run`


## Script mode to install as service

```
pip install Flask
pip install Flask-HTTPAuth


```