import requests
from requests.auth import HTTPDigestAuth
import xmltodict


def get_data(url:str, user:str, password:str):
    """
        Execute GET against given URL
        :global:
            USER:str - username
            PASSWORD:str - password credentials
        :args:
            url:str - BASE_URL + path
        :params:
            response:requests.GET - response from request
        :return:
            response content (decoded)
        """
    try:
        response = requests.get(
            url=url,
            auth=HTTPDigestAuth(user, password),
            verify=False  # keep disabled unless you add the cert
        )
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute GET against {url} (error: {error})")
    return response

def post(url:str, user:str, password:str):
    try:
        response = requests.post(
            url=url,
            auth=HTTPDigestAuth(user, password),
            verify=False  # keep disabled unless you add the cert
        )
        response.raise_for_status()
    except Exception as error:
        raise Exception(f"Failed to execute POST against {url} (error: {error})")

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

