import json
import camera_functions
import __support__

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


def create_mapping_policy(policy_name:str, dbms:str="bring [dbms]", table:str="bring [table]"):
    new_policy = {
        "mapping": {
            'id': policy_name,
            'name': policy_name,
            'dbms': dbms,
            'table': table,
            'schema': {
                "timestamp": {
                    "type": "timestamp",
                    "bring": "[timestamp]",
                    "default": "now()",
                    "apply": "epoch_to_datetime"
                },
                "object_id": {
                    "type": "string",
                    "bring": "[object_id]",
                    "default": ""
                },
                "object": {
                    "type": "string",
                    "bring": "[object]",
                    "default": ""
                },
                "active": {
                    "type": "bool",
                    "bring": "[active]",
                    "default": False
                },
                "start_time": {
                    "type": "timestamp",
                    "bring": "[start_time]",
                    "default": "now()"
                },
                "end_time": {
                    "type": "timestamp",
                    "bring": "[end_time]",
                    "default": "now()"
                },
                "recording": {
                    "type": "string",
                    "bring": "[recording]",
                    "default": ""
                },
                "recording_status": {
                    "type": "string",
                    "bring": "[recording_status]",
                    "default": "unknown"
                },
                'file': {
                    "blob": True,
                    "bring": "[snapshot]",
                    "extension": "jpeg",
                    "apply": "base64decoding",
                    "hash": "md5",
                    "type": "varchar"
                }
            }
        }
    }

    return json.dumps(new_policy)



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


def check_mqtt(anylog_conn:str, topic:str):
    output = False
    headers = {
        "command": f"get msg client where topic={topic}",
        "User-Agent": "AnyLog/1.23"
    }
    response = __support__.rest_request(method='GET', url=f"http://{anylog_conn}", headers=headers)
    if response.text.strip() not in ['No message client subscriptions', 'No such client subscription']:
        output = True
    return output


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


def publish_data(anylog_conn:str, payload:dict, topic:str='axies'):
    serialized_payload = json.dumps(payload)
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    __support__.rest_request(method='POST', url=f'http://{anylog_conn}', headers=headers,
                             data_payload=serialized_payload, stream=True, timeout=120)
