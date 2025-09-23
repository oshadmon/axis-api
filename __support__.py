import requests
from requests.auth import HTTPDigestAuth
import xmltodict

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def rest_request(method:str, url:str, headers:dict=None, data_payload:str=None, json_payload:dict=None, user:str=None, password:str=None, timeout:int=30):
    auth = HTTPDigestAuth(user, password) if user and password else None
    try:
        response = requests.request(method=method.upper(), url=url, headers=headers, data=data_payload,
                                    json=json_payload, auth=auth, timeout=timeout, verify=False)
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute {method.upper()} against {url} (Error: {error})")
    return response


def convert_xml(content:str)->dict:
    """
    Convert XML content to dict
    :args:
        content:str - XML content in string fromat
    :return:
        content as dict
    """
    try:
        return xmltodict.parse(content)
    except Exception as error:
        raise Exception(f"Failed to convert content from XML to dict")


def extract_credentials(conn_info:str)->(str, str, str):
    auth = None
    base_url = None
    user = None
    password = None

    if '@' in video_conn:
        auth, base_url = conn_info.split("@")
    else:
        return conn_info


    if auth and ':' in auth:
        user, password = auth.split(":")
    if not auth:
        raise ValueError(f"Video Connection format must be [USER:PASSWORD]@[IP:PORT]")

    return base_url, user, password
