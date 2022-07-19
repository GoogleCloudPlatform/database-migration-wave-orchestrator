# BMS BACKEND DEV


## Installation

Python version: 3.9

Install all the dependencies  with pip:

```
$ pip install -r requirements.txt
```

## Configuration:

* copy bms_app/local_config_sample.py to bms_app/local_config.py
* Edit bms_app/local_config.py

Another possible env variables:

- ` export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa-key.json ` to be able to work with GCP services locally
- `export FLASK_APP="bms_app:create_app('dev')"` - to be able to run `flask db ...` commands (Flask-Migrate==3.1.0)


## Development server

Run development server

```
python run.py
```

## Tests

```
pytest tests/
```


## Run Linter

```
pylint bms_app/
```
