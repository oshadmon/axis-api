import ast
from importlib.metadata import pass_none

from flask import Flask, jsonify
import __support__
import camera_functions

app = Flask(__name__)
BASE_URL = "166.143.227.89"
USER = "AnyLog"
PASSWORD = "OriIsTheBest#1!"

#--- Credentials --
def configure_client(base_url:str=None, user:str=None, password:str=None):
    """
    Update global config for Python client usage. Flask/browser requests will continue using defaults unless env vars
    are set.
    """
    global BASE_URL, USER, PASSWORD
    if base_url:
        BASE_URL = base_url
    if user:
        USER = user
    if password:
        PASSWORD = password


#--- Configurations --
@app.route("/config/status", methods=["GET"])
def get_status():
    output = camera_functions.camera_status(base_url=BASE_URL, user=USER, password=PASSWORD)
    if output is True:
        output = {"status": "Running"}
    else:
        output = {"status": "Not Running"}
    return jsonify(output)

@app.route("/config/info", methods=["GET"])
def get_configs():
    output = camera_functions.get_configs(base_url=BASE_URL, user=USER, password=PASSWORD)
    return jsonify(output)

@app.route("/config/geolocation", methods=["GET"])
def get_geolocation():
    output = camera_functions.get_geolocation(base_url=BASE_URL, user=USER, password=PASSWORD)
    return jsonify(output)

#--- Applications --
@app.route("/apps/list", methods=["GET"])
def get_app_list():
    output = camera_functions.list_applications(base_url=BASE_URL, user=USER, password=PASSWORD)
    return jsonify(output)

@app.route("/app/<app_name>", methods=["GET"])
def get_app_info(app_name:str):
    output = camera_functions.list_applications(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, status=False)
    return jsonify(output)

@app.route("/app/<app_name>/status", methods=["GET"])
def get_app_status(app_name:str):
    output = camera_functions.list_applications(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, status=True)
    return jsonify(output)

@app.route("/app/<app_name>/start", methods=["GET"])
def start_app(app_name:str):
    output = camera_functions.execute_application(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, command='start')
    return jsonify(output)

@app.route("/app/<app_name>/stop", methods=["GET"])
def stop_app(app_name:str):
    output = camera_functions.execute_application(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, command='stop')
    return jsonify(output)

@app.route("/app/<app_name>/restart", methods=["GET"])
def restart_app(app_name:str):
    output = camera_functions.execute_application(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, command='restart')
    return jsonify(output)


@app.route("/app/<app_name>/remove", methods=["GET"])
def remove_app(app_name:str):
    output = camera_functions.execute_application(base_url=BASE_URL, user=USER, password=PASSWORD, app_name=app_name, command='remove')
    return jsonify(output)


#--- Recordings --
@app.route("/recordings/list", methods=["GET"])
def list_recordings():
    output = camera_functions.list_recordings(base_url=BASE_URL, user=USER, password=PASSWORD, record_id=None)
    return jsonify(output)

@app.route("/recordings/<record_id>", methods=["GET"])
def recording_info(record_id:str=None):
    output = camera_functions.list_recordings(base_url=BASE_URL, user=USER, password=PASSWORD, record_id=record_id)
    return jsonify(output)

@app.route("/recordings/export/<record_id>", methods=["GET"])
def recording_export(record_id:str=None):
    return camera_functions.export_recording(base_url=BASE_URL, user=USER, password=PASSWORD, record_id=record_id)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
