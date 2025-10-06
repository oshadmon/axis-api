import __support__
import camera_functions
import json
from camera_functions import list_recordings

#---- Create Policies ---
def create_camera_policy(base_url:str, user:str, password:str):
    """
    Create camera information policy
    :args:
        base_url:str - base URL
        user:str | password:str - authentication information
    :params:
        geolocation:dict - location information
        camera_info:dict - camera information
        new_policy:dict - combined geolocation + camera Info
    :return:
        new_policy
    :sample-policy:
    {
        "camera": {
            "Architecture": "aarch64",
            "ProdNbr": "P12-MkIII",
            "HardwareID": "9A5",
            "ProdFullName": "AXIS P12 Mk III Main Unit",
            "Version": "12.6.85",
            "ProdType": "Modular Camera",
            "SocSerialNumber": "AEA03B5C-B1384AD6-F5C84A12-58C8D5CB",
            "Soc": "Ambarella CV25",
            "Brand": "AXIS",
            "WebURL": "http://www.axis.com",
            "ProdVariant": "",
            "SerialNumber": "B8A44FC5C075",
            "ProdShortName": "AXIS P12 Mk III",
            "BuildDate": "Sep 11 2025 17:26",
            "loc": "0.0, 0.0"
        }
    }
    """
    geolocation = camera_functions.get_geolocation(base_url=base_url, user=user, password=password)
    camera_info = camera_functions.get_configs(base_url=base_url, user=user, password=password)
    serial_num = camera_info['SerialNumber']

    camera_info = {__support__.camel_to_snake(key): value for key, value in camera_info.items()}
    camera_info['loc'] = f"{geolocation['lat']}, {geolocation['long']}"

    new_policy = {
        "camera": camera_info
    }

    return json.dumps(new_policy), serial_num

def create_camera_mapping_policy(policy_name:str, dbms:str="bring [dbms]", table:str="bring [table]")->str:
    """
    Generate policy to accept data from Axis camera
    :args:
        policy_name:str - policy_name - used as policy ID
        dbms:str - logical database to store data in
        table:str - logical table to store data in
    :params:
         new_policy:str - generate mapping policy
    :return:
        serialized policy
    :generated policy:
    {
      "mapping": {
        "id": "axis-data",
        "dbms": "bring [dbms]",
        "table": "bring [table]",
        "schema": {
            "video_id": {"type": "string", "bring": "[video_id]"},
            "timestamp": {"type": "timestamp", "default": "now()"},
            "start_time": {"type": "timestamp", "bring": "[start_time]"},
            "end_time": {"type": "timestamp", "bring": "[end_time]"},
            "source": {"type": "string", "bring": "[source]"},
            "file_type": {"type": "string", "bring": "[file_type]"},
            "file": {"blob": true, "bring": "[content]", "extension": "mp4",
                    "apply": "base64decoding", "hash": "md5", "type": "varchar"},
            "video_resolution": {"type": "string", "bring": "[resolution]"},
            "video_width": {"type": "string", "bring": "[width]"},
            "video_height": {"type": "string", "bring": "[height]"}
        }
      }
    }
    :sample-data:
    {
        "video_id": "20250923_131503_2072_B8A44FC5C075",
        "start_time": "2025-09-23T17:15:03.566530Z",
        "end_time": "2025-09-23T17:16:19.490419Z",
        "source": "2",
        "content": "VlqUVfAp0PcA0+PcFo8KAka0TBS2JABT3RcU03x5LO9eeoBZhCU5l1DkgqI7+ERGSNO5WF6hIRG9",
        "file_type": "video/mp4",
        "video_resolution": "1920x1080",
        "video_width": "1920",
        "video_height": "1080"

    }
    """
    new_policy = {"mapping": {
        "id": policy_name,
        "name": f"{policy_name}-mapping",
        "dbms": dbms,
        "table": table,
        "schema": {
            "timestamp": {"type": "timestamp", "default": "now()"},
            "video_id": {"type": "string", "bring": "[video_id]"},
            "start_time": {"type": "timestamp", "bring": "[start_time]"},
            "end_time": {"type": "timestamp", "bring": "[end_time]"},
            "source": {"type": "string", "bring": "[source]"},
            "file_type": {"type": "string", "bring": "[file_type]"},
            "file": {"blob": True, "bring": "[content]", "extension": "mp4",
                     "apply": "base64decoding", "hash": "md5", "type": "varchar"},
            "video_resolution": {"type": "string", "bring": "[video_resolution]"},
            "video_width": {"type": "string", "bring": "[video_width]"},
            "video_height": {"type": "string", "bring": "[video_height]"}
        }
    }}

    return json.dumps(new_policy)


def create_data_mapping_policy(policy_name:str, dbms:str="bring [dbms]", table:str="bring [table]")->str:
    """
    Generate policy to accept data from Axis camera
    :args:
        policy_name:str - policy_name - used as policy ID
        dbms:str - logical database to store data in
        table:str - logical table to store data in
    :params:
         new_policy:str - generate mapping policy
    :return:
        serialized policy
    :sample-data:
        {
            "topic":"axis:CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY",
            "timestamp":1759713693673,
            "serial":"B8A44FC5C075",
            "message":{
                "source":{},
                "key":{},
                "data":{
                    "objectId":"370312",
                    "active":"0",
                    "classTypes":"human",
                    "triggerTime":"2025-10-05T21:21:33.856-0400"
                }
            }
        }
    :generated policy:
    {
      "mapping": {
        "id": "axis-data",
        "dbms": "bring [dbms]",
        "table": "bring [table]",
        "schema": {
            "video_id": {"type": "string", "bring": "[video_id]"},
            "timestamp": {"type": "timestamp", "default": "now()"},
            "start_time": {"type": "timestamp", "bring": "[start_time]"},
            "end_time": {"type": "timestamp", "bring": "[end_time]"},
            "source": {"type": "string", "bring": "[source]"},
            "file_type": {"type": "string", "bring": "[file_type]"},
            "file": {"blob": true, "bring": "[content]", "extension": "mp4",
                    "apply": "base64decoding", "hash": "md5", "type": "varchar"},
            "video_resolution": {"type": "string", "bring": "[resolution]"},
            "video_width": {"type": "string", "bring": "[width]"},
            "video_height": {"type": "string", "bring": "[height]"}
        }
      }
    }
    :sample-data:
    {
        "video_id": "20250923_131503_2072_B8A44FC5C075",
        "start_time": "2025-09-23T17:15:03.566530Z",
        "end_time": "2025-09-23T17:16:19.490419Z",
        "source": "2",
        "content": "VlqUVfAp0PcA0+PcFo8KAka0TBS2JABT3RcU03x5LO9eeoBZhCU5l1DkgqI7+ERGSNO5WF6hIRG9",
        "file_type": "video/mp4",
        "video_resolution": "1920x1080",
        "video_width": "1920",
        "video_height": "1080"

    }
    """
    new_policy = {"mapping": {
        "id": policy_name,
        "name": policy_name,
        "dbms": dbms,
        "table": table,
        "readings": "message",
         "schema": {
             "timestamp": {
                 "bring": "[timestamp]",
                 "default": "now()",
                 "type": "timestamp",
                 "apply": "epoch_to_datetime",
                 "root": True
             },
             "serial": {
                 "bring": "[serial]",
                 "default": "",
                 "type": "string",
                 "root": True
             },
             "object_id": {
                 "bring": "[data][objectId]",
                 "type": "int"
             },
             "active": { # 0 (False) if not active | 1 (True) if active <- not supported @ this time
                 "bring": "[data][active]",
                 "default": 0,
                 "type": "int"
             },
             "class_type": {
                 "bring": "[data][classTypes]",
                 "default": "",
                 "type": "string"
             }
        }
    }}

    return json.dumps(new_policy)

def check_policy(anylog_conn:str, where_condition:dict={})->bool:
    """
    Check whether a policy exists based on policy ID
    :args:
        anylog_conn:str - AnyLog REST connection information
        policy_id:str - policy ID to check
    :params:
        status:bool
    :return:
        if exists return True else False
    """
    status = False
    request_cmd = f"blockchain get *"
    if where_condition:
        request_cmd += " where "
        for condition in where_condition:
            request_cmd += f'{condition}={where_condition[condition]} and'
        request_cmd = request_cmd.rsplit(" and", 1)[0]

    headers = {
        "command": request_cmd,
        "User-Agent": "AnyLog/1.23"
    }
    response = __support__.rest_request(method='GET', url=f"http://{anylog_conn}", headers=headers)
    try:
        if response.json():
            status = True
    except:
        pass

    return status

def declare_policy(raw_policy, anylog_conn:str):
    """
    REST process to declare policy on the blockchain
    """
    new_policy = f"<new_policy={raw_policy}>"
    headers = {
        'command': 'blockchain insert where policy=!new_policy and local=true and master=!ledger_conn',
        'User-Agent': 'AnyLog/1.23'
    }
    __support__.rest_request(method='POST', url=f"http://{anylog_conn}", headers=headers, data_payload=new_policy)


#--- REST POST Client ---
def declare_mqtt_request(anylog_conn:str, broker:str, topic:str, policy_id:str, port:int=None, user:str=None, password:str=None):
    request_cmd = f"run msg client where broker={broker} "

    if port:
        request_cmd += f"and port={port} "
    if broker == "rest":
        request_cmd += "and user-agent=anylog "
    if user:
        request_cmd += f"and user={user} "
    if password:
        request_cmd += f"and password={password} "

    request_cmd += f"and log=false and topic=(name={topic} and policy={policy_id})"

    headers = {
        "command": request_cmd,
        "User-Agent": "AnyLog/1.23"
    }
    response = __support__.rest_request(method='POST', url=f"http://{anylog_conn}", headers=headers)
    return response

def generate_data(base_url:str, user:str, password:str, record_id:str):
    data = list_recordings(base_url=base_url, user=user, password=password, record_id=record_id)
    payload = {
        "video_id": record_id,
        "start_time": data['@starttime'],
        "end_time": data['@stoptime'],
        "source": data['@source'],
        "video_resolution": data['video']['@resolution'],
        "video_width": data['video']['@width'],
        "video_height": data['video']['@height']
    }
    return payload


#--- Data publishing ---
def publish_data(anylog_conn:str, payload:dict, topic:str='axies'):
    serialized_payload = json.dumps(payload)
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    __support__.rest_request(method='POST', url=f'http://{anylog_conn}', headers=headers,
                             data_payload=serialized_payload, stream=True)
