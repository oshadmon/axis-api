import re
import requests
from requests.auth import HTTPDigestAuth
import xmltodict
import datetime

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def rest_request(method:str, url:str, headers:dict=None, data_payload:str=None, json_payload:dict=None, user:str=None,
                 password:str=None, timeout:int=30, stream:bool=False):
    """
    Execute REST request
    :args:
        method:str - request method type (POST / GET)
        url:str - URL to send request against
        headers:dict - REST headers
        data_payload:str - serialized payload
        json_payload:dict - non-serialized payload
        user:str | password:str - authentication credentials for REST request
        timeout:int - REST timeout
        stream:bool - stream results
    :params:
        auth:HTTPDigestAuth - authentication for request
        response:requests.Request - request response
    :return:
        response
    """
    auth = HTTPDigestAuth(user, password) if user and password else None
    try:
        response = requests.request(method=method.upper(), url=url, headers=headers, data=data_payload,
                                    json=json_payload, auth=auth, timeout=timeout, verify=False, stream=stream)
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
    """
    Extract credentials based on conn_info
    """
    auth = None
    base_url = None
    user = None
    password = None

    if '@' in conn_info:
        auth, base_url = conn_info.split("@")
    else:
        return conn_info


    if auth and ':' in auth:
        user, password = auth.split(":")
    if not auth:
        raise ValueError(f"Video Connection format must be [USER:PASSWORD]@[IP:PORT]")

    return base_url, user, password

def camel_to_snake(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def validate_timestamp_format(timestamp:str):
    """
    Convert string timestamp to datetime format
    """
    formats = {
        "%Y-%m-%d %H:%M:%S": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\s([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        "%Y-%m-%dT%H:%M:%S": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        "%Y-%m-%dT%H:%M:%SZ": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)Z$',
        "%Y-%m-%d %H:%M:%S.%f": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\s([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.\d+$',
        "%Y-%m-%dT%H:%M:%S.%fZ": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.\d+Z$'
    }

    output = None
    if timestamp:
        for frmt, regex in formats.items():
            if re.match(regex, timestamp):
                output = datetime.datetime.strptime(timestamp, frmt)
    return output
