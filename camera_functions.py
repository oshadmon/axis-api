import ast
import os

from __support__ import rest_request, convert_xml, validate_timestamp_format, sort_timestamps

#--- Configurations --
def camera_status(base_url:str, user:str, password:str):
    status = False
    url = f"{base_url}/axis-cgi/systemready.cgi"
    if not base_url.startswith('http'):
        url = f'https://{url}'
    response = rest_request(method='POST', url=url,
                            headers={"Content-Type": "application/json"},
                            json_payload={
                                "apiVersion": "1.1", "context": "my context", "method": "systemready",
                                "params": {"timeout": 20}
                            },
                            user=user, password=password)

    try:
        if response.json()['data']['systemready'].strip().lower() == 'yes':
            status = True
    except:
        pass
    return status

def get_configs(base_url:str, user:str, password:str):
    """
    Get camera configurations
    :args:
        base_url:str - IP:port of the camera
        user:str | password:str - credentials
    :params:
        url:str - URL path
        response:requests - response from request
    :return:
        dict of information
    """
    url = f'{base_url}/axis-cgi/basicdeviceinfo.cgi'
    if not base_url.startswith('http'):
        url = f'https://{url}'

    response = rest_request(method='POST', url=url, headers={"Content-Type": "application/json"},
                            json_payload={"apiVersion": "1.0", "context": "flask-client", "method": "getAllProperties"},
                            user=user, password=password)

    try:
        return ast.literal_eval(response.content.decode())['data']['propertyList']
    except Exception as error:
        raise Exception(f"Failed to parse content from {url} (Error: {error})")

def get_geolocation(base_url:str, user:str, password:str):
    url = f"{base_url}/axis-cgi/geolocation/get.cgi"
    if not base_url.startswith('http'):
        url = f'https://{url}'
    response = rest_request(method='GET', url=url, user=user, password=password)

    content = convert_xml(content=response.content.decode())
    if content:
        return {
            "lat": float(content['PositionResponse']['Success']['GetSuccess']['Location']['Lat']),
            "long": float(content['PositionResponse']['Success']['GetSuccess']['Location']['Lng'])
        }
    return {}

#--- Applications --
def __get_applications(base_url:str, user:str, password:str):
    applications = []
    url = f"{base_url}/axis-cgi/applications/list.cgi"
    if not base_url.startswith('http'):
        url = f'https://{url}'
    response = rest_request(method='GET', url=url, user=user, password=password)
    content = convert_xml(content=response.content.decode())
    if content and content['reply']['@result'] == 'ok':
            try:
                applications = content['reply']['application']
            except Exception:
                pass

    return  applications

def list_applications(base_url:str, user:str, password:str, app_name:str=None, status:bool=False):
    applications = __get_applications(base_url=base_url, user=user, password=password)
    if applications and app_name:
        for app in applications:
            if app['@Name'] == app_name:
                return {"status": app["@Status"]} if status is True else app
    return applications

def execute_application(base_url:str, user:str, password:str, app_name:str, command:str):
    url = f"{base_url}/axis-cgi/applications/control.cgi?package={app_name}&action={command}"
    if not base_url.startswith('http'):
        url = f'https://{url}'
    rest_request(method='POST', url=url, user=user, password=password)
    return list_applications(base_url=base_url, user=user, password=password, app_name=app_name, status=True)

#--- Recordings ---
def __get_recordings(base_url:str, user:str, password:str):
    url = f"{base_url}/axis-cgi/record/list.cgi?recordingid=all"
    if not url.startswith('http'):
        url = f"https://{url}"
    videos = []
    response = rest_request(method='GET', url=url, user=user, password=password)
    content = convert_xml(content=response.content.decode())
    if content:
        for user in list(content.keys()):
            if 'recordings' in content[user] and 'recording' in content[user]['recordings']:
                videos += content[user]['recordings']['recording']

    return videos

def list_recordings(base_url:str, user:str, password:str, record_id:str=None):
    recordings = __get_recordings(base_url=base_url, user=user, password=password)
    if record_id:
        for recording in recordings:
            if recording['@recordingid'] == record_id:
                return recording
        return []
    return recordings

def export_recording(base_url:str, user:str, password:str, record_id:str):
    recording = list_recordings(base_url=base_url, user=user, password=password, record_id=record_id)
    if not recording:
        return {"Error": f"Failed to locate image with ID {record_id}"}

    url = f"{base_url}/axis-cgi/record/export/exportrecording.cgi?schemaversion=1&recordingid={record_id}&exportformat=matroska&diskid={recording['@diskid']}"
    if not base_url.startswith('http'):
        url = f"https://{url}"

    response = rest_request(method='GET', url=url, user=user, password=password, timeout=120, stream=True)
    if not 200 <= int(response.status_code) < 300:
        return {"Error": f"Failed to execute due to network error {response.status_code}"}

    return (
        response.content,
        200,
        {
            "Content-Type": "video/mp4",
            "Content-Disposition": "inline"  # let browser decide how to display
        },
    )

# def get_recording_id(base_url:str, user:str, password:str, timestamp:str):
#     current_dt = validate_timestamp_format(timestamp)
#     if not current_dt:
#         return None
#
#     recordings  = list_recordings(base_url=base_url, user=user, password=password)
#     recordings = sort_timestamps(recordings=recordings, newest=True)
#     recording_id = recordings[0].get('@recordingid')
#
#     for recording in recordings:
#         start = validate_timestamp_format(recording.get('@starttimelocal'))
#         end = validate_timestamp_format(recording.get('@stoptimelocal'))
#         if (start and end) and start <= current_dt <= end:
#             recording_id = recording.get('@recordingid')
#         elif (start and not end) and  start <= current_dt:
#             recording_id = recording.get('@recordingid')
#
#     return recording_id



#---- Analytics ---
def get_scenerios(base_url:str, user:str, password:str):
    url = f"{base_url}/axis-cgi/applications/control.cgi"
    if not base_url.startswith('http'):
        url = f"https://{url}"

    payload = {
        "apiVersion": "1.1",
        "context": "my context",
        "method": "getConfiguration"
    }

    response = rest_request(method='POST', url=url, user=user, password=password, json_payload=payload, stream=True)
    print(response)

def get_analytics(base_url:str, user:str, password:str):
    url = f"{base_url}/local/objectanalytics/control.cgi"
    if not base_url.startswith('http'):
        url = f"https://{url}"

    start_time = "2025-09-23T23:45:04"
    end_time = "2025-09-23T23:46:19"
    payload = {
        "apiVersion": "1.1",
        "method": "getAccumulatedCounts",
        "params": {
            "scenario": "Scenario1",
            "startTime": start_time,
            "endTime": end_time,
            "objects": ["Bus", "Car", "Bike", "Truck", "Other"]
        }
    }

    response = rest_request(method='POST', url=url, user=user, password=password, json_payload=payload)
    print(response)

def take_snapshot(base_url:str, user:str, password:str):
    """
    Capture a snapshot image from the Axis camera
    """
    url = f"{base_url}/axis-cgi/jpg/image.cgi"
    if not base_url.startswith("http"):
        url = f"https://{url}"
    response = rest_request(method="GET", url=url, user=user, password=password, stream=True)
    if not 200 <= int(response.status_code) < 300:
        raise Exception(f"Failed to capture snapshot (HTTP {response.status_code})")

    return response.content

    # return f"Snapshot saved to {filename}"

#--- Other functions ---
def id_by_timestamp(base_url:str, user:str, password:str, timestamp:str):
    current_dt = validate_timestamp_format(timestamp)
    if not current_dt:
        return None

    recordings  = list_recordings(base_url=base_url, user=user, password=password)
    recordings = sort_timestamps(recordings)
    recording_id = recordings[0].get('@recordingid')

    for recording in recordings:
        start = validate_timestamp_format(recording.get('@starttimelocal'))
        end = validate_timestamp_format(recording.get('@stoptimelocal'))
        if (start and end) and start <= current_dt <= end:
            recording_id = recording.get('@recordingid')
        elif (start and not end) and  start <= current_dt:
            recording_id = recording.get('@recordingid')

    return recording_id
