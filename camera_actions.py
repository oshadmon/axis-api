import os
from flask import Flask, jsonify
import camera_functions
from __support__ import extract_credentials
app = Flask(__name__)

BASE_URL = "166.143.227.89"
USER = "AnyLog"
PASSWORD = "OriIsTheBest#1!"

#--- Credentials --
def configure_client(camera_conn:str=None):
    """
    Extract camera credentials from ENV variable or user_input param
    :args:
        camera_conn:str - camera connection through user input or env param (USER:PASS@IP:PORT)
    :global:
        BASE_URL:str
        USER:str
        PASSWORD:str
    """
    global BASE_URL, USER, PASSWORD
    if os.getenv('CAMERA_CONN'):
        BASE_URL, USER, PASSWORD = extract_credentials(conn_info=os.getenv('CAMERA_CONN'))
    elif camera_conn:
        BASE_URL, USER, PASSWORD = extract_credentials(conn_info=camera_conn)

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
@app.route("/app/list", methods=["GET"])
def get_app_list():
    apps_list = []
    output = camera_functions.list_applications(base_url=BASE_URL, user=USER, password=PASSWORD)
    if output:
        for this_app in output:
            apps_list.append(this_app['@Name'])
    return jsonify(apps_list)


@app.route("/app/<app_name>/info", methods=["GET"])
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

@app.route("/sys-logs", methods=["GET"])
def get_syslogs():
    return camera_functions.get_syslogs(base_url=BASE_URL, user=USER, password=PASSWORD)

@app.route("/event-logs", methods=["GET"])
def get_eventlogs():
    return camera_functions.get_eventlogs(base_url=BASE_URL, user=USER, password=PASSWORD)

@app.route("/crash-logs", methods=["GET"])
def get_crashlogs():
    return camera_functions.get_crashlogs(base_url=BASE_URL, user=USER, password=PASSWORD)


@app.route("/snapshot", methods=["GET"])
def snapshot():
    return camera_functions.take_snapshot(base_url=BASE_URL, user=USER, password=PASSWORD)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
