import ast
from flask import Flask, jsonify


import __support__

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


def fetch_videos()->list:
    """
    Fetch list of applications from Camera
    :params:
        url:str - built URL
        applications:list - list of applications
        response:requests.GET - response from GET
        content:dict - response converted from XML to JSON
    :return:
        list of applications
    :sample video info:
    {
        "@diskid":"SD_DISK",
        "@eventid":"Motion Recording",
        "@eventtrigger":"Record video while the rule is active",
        "@locked":"No",
        "@recordingid":"20250921_164046_B0AB_B8A44FC5C075",
        "@recordingstatus":"recording",
        "@recordingtype":"triggered",
        "@source":"2",
        "@starttime":"2025-09-21T20:40:46.627753Z",
        "@starttimelocal":"2025-09-21T16:40:46.627753-04:00",
        "@stoptime":"",
        "@stoptimelocal":"",
        "video":{
            "@framerate":"15:1",
            "@height":"1080",
            "@mimetype":"video/x-h264",
            "@resolution":"1920x1080",
            "@source":"2","@width":"1920"
        }
    }
    """
    url = f"{BASE_URL}/axis-cgi/record/list.cgi?recordingid=all"
    videos = {}

    response = __support__.get_data(url=url, user=USER, password=PASSWORD)
    if 200 <= response.status_code < 300:
        content = __support__.convert_xml(content=response.content.decode())
        if content:
            for user in list(content.keys()):
                if 'recordings' in content[user] and 'recording' in content[user]['recordings']:
                    videos[user] = content[user]['recordings']['recording']

    return videos

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
    """
    Get status for a specific app
    :args:
        app_name:str - application name
    :params:
        applications:list - list of applications
    :return:
        application status if exists - if not "Unknown"
    """
    applications = fetch_applications()
    for this_app in applications:
        if this_app["@Name"] == app_name:
            return jsonify({"status": this_app["@Status"]})

    return jsonify({"status": "Unknown"}), 404

@app.route("/execute/<app_name>/start", methods=["GET"])
def application_start(app_name:str):
    """
    Based on app_name start application
    :return:
        application status
    """
    execute_application(app_name=app_name, cmd='start')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/stop", methods=["GET"])
def application_stop(app_name:str):
    """
    Based on app_name stop application
    :return:
        application status
    """
    execute_application(app_name=app_name, cmd='stop')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/restart", methods=["GET"])
def application_restart(app_name:str):
    """
    Based on app_name restart application
    :return:
        application status
    """
    execute_application(app_name=app_name, cmd='restart')
    return application_status(app_name=app_name)

@app.route("/execute/<app_name>/remove", methods=["GET"])
def application_remove(app_name:str):
    """
    Based on app_name remove application
    :return:
        application status
    """
    execute_application(app_name=app_name, cmd='start')
    return application_status(app_name=app_name)

@app.route("/feed/list", methods=["GET"])
@app.route("/feed/list/<record_id>", methods=["GET"])
def list_videos(record_id:str=None):
    response = fetch_videos()
    if record_id:
        for user in response:
            for video in response[user]:
                if record_id == video['@recordingid']:
                    return jsonify(video)

    return jsonify(response)

@app.route("/feed/export/<record_id>", methods=["GET"])
def export_recording(record_id):

    image_info = list_videos(record_id)
    if not image_info:
        return jsonify({"Error": f"Failed to locate image with ID {record_id}"})
    image_info = ast.literal_eval(image_info.data.decode())

    url = f"{BASE_URL}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={record_id}&exportformat=matroska&diskid={image_info['@diskid']}"
    response = __support__.get_data(url=url, user=USER, password=PASSWORD)
    if not 200 <= int(response.status_code) < 300:
        return jsonify({"Error": f"Failed to execute due to network error {response.status_code}"})

    return (
        response.content,
        200,
        {
            "Content-Type": "video/mp4",
            "Content-Disposition": "inline"  # let browser decide how to display
        },
    )

    # url = f"{BASE_URL}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={record_id}"
    # response = __support__.get_data(url=url, user=USER, password=PASSWORD)
    # print(response)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
