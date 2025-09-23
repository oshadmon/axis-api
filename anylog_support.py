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

def create_mapping_policy(policy_name:str, dbms:str="bring [dbms]", table:str="bring [table]")->str:
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
        "video_id": "bring [video_id]",
        "timestamp": {"type": "timestamp", "default": "now()"},
        "start_time": {"type": "timestamp", "bring": "[start_time]"},
        "end_time": {"type": "timestamp", "bring": "[end_time]"},
        "source": {"type": "string", "bring": "[source]"},
        "file_type": {"type": "string", "bring": "[file_type]"},
        "file": {"blob": true, "bring": "[content]", "extension": "mp4",
                "apply": "base64decoding", "hash": "md5", "type": "varchar"},
        "readings": "video",
        "schema": {
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
        "file_type": "video/mp4"
        "video": {
            "resolution": "1920x1080",
            "width": "1920",
            "height": "1080"
        }
    }
    """
    new_policy = {"mapping": {
        "id": policy_name,
        "dbms": dbms,
        "table": table,
        "video_id": "bring [video_id]",
        "timestamp": {"type": "timestamp",  "default": "now()"},
        "start_time": {"type": "timestamp", "bring": "[start_time]"},
        "end_time": {"type": "timestamp", "bring": "[end_time]"},
        "source": {"type": "string", "bring": "[source]"},
        "file_type": {"type": "string", "bring": "[file_type]"},
        "file": {"blob": True, "bring": "[content]", "extension": "mp4",
                 "apply": "base64decoding", "hash": "md5", "type": "varchar"},
        "readings": "video",
        "schema": {
            "video_resolution": {"type": "string", "bring": "[resolution]"},
            "video_width": {"type": "string", "bring": "[width]"},
            "video_height": {"type": "string", "bring": "[height]"}
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

def declare_policy(raw_policy, anylog_conn:str, ledger_conn:str):
    new_policy = f"<new_policy={raw_policy}>"
    headers = {
        'command': 'blockchain insert where policy=!new_policy and local=true and master=!ledger_conn',
        'User-Agent': 'AnyLog/1.23',
        'destination': ledger_conn
    }
    __support__.rest_request(method='POST', url=f"http://{anylog_conn}", headers=headers, data_payload=new_policy)


#--- REST POST Client ---
def declare_mqtt_request(anylog_conn:str, topic:str):
    request_cmd = f"run msg client where broker=rest and user-agent=anylog and log=false and topic=(name={topic} and policy={topic})"
    headers = {
        "command": request_cmd,
        "User-Agent": "AnyLog/1.23"
    }
    response = __support__.rest_request(method='POST', url=f"http://{anylog_conn}", headers=headers)


def generate_data(base_url:str, user:str, password:str, record_id:str):
    data = list_recordings(base_url=base_url, user=user, password=password, record_id=record_id)
    payload = {
        "video_id": record_id,
        "start_time": data['@starttime'],
        "end_time": data['@stoptime'],
        "source": data['@source'],
        "video": {
            "resolution": data['video']['@resolution'],
            "width": data['video']['@width'],
            "height": data['video']['@height']
        }
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

    __support__.rest_request(method='POST', url=f'http://{anylog_conn}', headers=headers, data_payload=serialized_payload)
