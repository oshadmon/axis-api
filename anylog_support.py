import __support__
import camera_functions
import json
from camera_functions import list_recordings

def create_policy(base_url:str, user:str, password:str):
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

    camera_info['loc'] = f"{geolocation['lat']}, {geolocation['long']}"
    new_policy = {
        "camera": camera_info
    }

    return new_policy


def declare_policy(anylog_conn:str, ledger_conn:str, base_url:str, user:str, password:str):
    raw_policy = create_policy(base_url=base_url, user=user, password=password)
    new_policy = f"<new_policy={json.dumps(raw_policy)}>"
    headers = {
        'command': 'blockchain insert where policy=!new_policy and local=true and master=!ledger_conn',
        'User-Agent': 'AnyLog/1.23',
        'destination': ledger_conn
    }
    __support__.rest_request(method='POST', url=f"http://{anylog_conn}", headers=headers, data_payload=new_policy)


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


def publish_data(anylog_conn:str, payload:dict, topic:str='axies', dbms:str='axis', table:str='camera1', serialized=None):
    payload['dbms'] = dbms
    payload['table'] = table

    serialized_payload = json.dumps(payload)
    headers = {
        'command': 'data',
        'topic': topic,
        'User-Agent': 'AnyLog/1.23',
        'Content-Type': 'text/plain'
    }

    __support__.rest_request(method='POST', url=f'http://{anylog_conn}', headers=headers, data_payload=serialized_payload)
