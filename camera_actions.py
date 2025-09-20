import __support__
from flask import Flask, jsonify

app = Flask(__name__)
BASE_URL = "https://166.143.227.89"
USER = "AnyLog"
PASSWORD = "OriIsTheBest#1!"

# --- Helper function ---
def fetch_applications()->list:
    """
    Fetch list of applications from Camera
    :params:
        url:str - built URL
        applications:list - list of applications
        response:requests.GET - response from GET
        content:dict - response converted from XML to JSON
    :return:
        list of applications
    """
    url = f"{BASE_URL}/axis-cgi/applications/list.cgi"
    applications = []

    response = __support__.get_data(url=url, user=USER, password=PASSWORD)
    if 200 <= response.status_code < 300:
        content = __support__.convert_xml(content=response.content.decode())
        if content and content['reply']['@result'] == 'ok':
            try:
                applications = content['reply']['application']
            except Exception:
                pass

    return applications

def execute_application(app_name:str, cmd:str):
    """
    Execute command against the camera
    :args:
        app_name:str - app to execute request against
        cmd:str - command to execute (start, stop, remove, restart)
    :params:
        url:str - generated URL
    :return:
        request for POST
    """
    url = f"{BASE_URL}/axis-cgi/applications/control.cgi?package={app_name}&action={cmd}"
    return __support__.post(url=url, user=USER, password=PASSWORD)


# --- Routes ---
@app.route("/list", methods=["GET"])
@app.route("/list/<app_name>", methods=["GET"])
def applications_list(app_name=None):
    """
    List applications and optionally specific application object(s)
    :args:
        app_name:str - specific application to get info for
    :return:
        application(s) information
    """
    applications = fetch_applications()

    if app_name:
        for this_app in applications:
            if this_app['@Name'] == app_name:
                return jsonify(this_app)
        return jsonify({"error": "Application not found"}), 404

    return jsonify(applications)


@app.route("/status/<app_name>", methods=["GET"])
def application_status(app_name:str):
    applications = fetch_applications()
    for this_app in applications:
        if this_app["@Name"] == app_name:
            return jsonify({"status": this_app["@Status"]})

    return jsonify({"status": "Unknown"}), 404

@app.route("/execute/<app_name>/start", methods=["GET"])
def application_start(app_name:str):
    execute_application(app_name=app_name, cmd='start')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/stop", methods=["GET"])
def application_stop(app_name:str):
    execute_application(app_name=app_name, cmd='stop')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/restart", methods=["GET"])
def application_restart(app_name:str):
    execute_application(app_name=app_name, cmd='restart')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/remove", methods=["GET"])
def application_remove(app_name:str):
    execute_application(app_name=app_name, cmd='start')
    return application_status(app_name=app_name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
