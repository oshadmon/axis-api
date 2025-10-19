import re
from requests.auth import HTTPDigestAuth
import requests
import xmltodict
import datetime


def camel_to_snake(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def extract_credentials(conn_info:str)->(str, str, str):
    """
    Extract credentials based on conn_info
    """
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
    response = rest_request(method='GET', url=f"http://{anylog_conn}", headers=headers)
    try:
        if response.json():
            status = True
    except:
        pass

    return status


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


def sort_timestamps(recordings:list, key_name:str='@starttimelocal', newest:bool=True):
    for recording_loc in range(len(recordings)):
        recordings[recording_loc][key_name] = validate_timestamp_format(timestamp=recordings[recording_loc][key_name])

    valid_recordings = [r for r in recordings if r[key_name] is not None]
    valid_recordings.sort(key=lambda x: x[key_name], reverse=newest)
    return valid_recordings


def validate_timestamp_format(timestamp:(str or datetime.datetime)):
    """
    Convert string timestamp to datetime format
    """
    if isinstance(timestamp, datetime.datetime):
        return timestamp
    formats = {
        "%Y-%m-%d %H:%M:%S": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\s([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        "%Y-%m-%dT%H:%M:%S": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        "%Y-%m-%dT%H:%M:%SZ": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)Z$',
        "%Y-%m-%d %H:%M:%S.%f": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])\s([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.\d+$',
        "%Y-%m-%dT%H:%M:%S.%fZ": r'^(\d{4})-(0[1-9]|1[0-2])-([0-2]\d|3[01])T([01]\d|2[0-3]):([0-5]\d):([0-5]\d)\.\d+Z$',
        "%Y-%m-%dT%H:%M:%S.%f%z": [
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?[+-]\d{4}$"
        ]
    }
    if timestamp:
        for frmt, regex in formats.items():
            if isinstance(regex, list):
                # multiple regexes for this format
                for r in regex:
                    if re.fullmatch(r, timestamp):
                        ts = timestamp
                        # handle offset with colon for %z
                        if '%z' in frmt and ts[-3] == ':':
                            ts = ts[:-3] + ts[-2:]  # convert -04:00 -> -0400
                        return datetime.datetime.strptime(ts, frmt)
            else:
                if re.fullmatch(regex, timestamp):
                    ts = timestamp
                    # handle Z as +0000 for %z
                    if frmt.endswith('Z'):
                        ts = ts.replace('Z', '+0000')
                        frmt = frmt.replace('Z', '%z')
                    return datetime.datetime.strptime(ts, frmt)

    return None

def convert_to_utc(timestamp:(str or datetime.datetime)):
    if timestamp == 'now':
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    updated_ts = validate_timestamp_format(timestamp=timestamp) # convert to datetime format
    if not updated_ts:
        raise ValueError("Invalid timestamp format")
    utc_timestamp = updated_ts.replace(tzinfo=datetime.timezone.utc) if not updated_ts.tzinfo else updated_ts.astimezone(datetime.timezone.utc)
    return utc_timestamp



def parse_logs(content:str):
    log_text = content.strip().splitlines()
    raw_dicts = [{"line_number": i + 1, "message": line} for i, line in enumerate(log_text) if
                 line not in ["", "----- System log -----"]]

    log_pattern = re.compile(
        r"^(?:(?P<timestamp>\S+) )?"
        r"(?:(?P<host>\S+) )?"
        r"(?:\[ (?P<level>\w+) \] )?"
        r"(?:(?P<subsystem>\w+): )?"
        r"(?P<message>.+)$"
    )

    parsed_logs = []
    for raw_dict in raw_dicts:
        match = log_pattern.match(raw_dict['message'])
        if match:
            parsed_logs.append(match.groupdict())

    return parsed_logs


def detection_count(objects:list)->dict:
    objects_dict = {}
    for object in objects:
        if object not in objects_dict:
            objects_dict[object] = 0
        objects_dict[object] += 1
    return objects_dict