from __support__ import rest_request, convert_xml

import ast

#--- Configurations --
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
    url = f'https://{base_url}/axis-cgi/basicdeviceinfo.cgi'
    response = rest_request(method='POST', url=url, headers={"Content-Type": "application/json"},
                            json_payload={"apiVersion": "1.0", "context": "flask-client", "method": "getAllProperties"},
                            user=user, password=password)

    try:
        return ast.literal_eval(response.content.decode())['data']['propertyList']
    except Exception as error:
        raise Exception(f"Failed to parse content from {url} (Error: {error})")

def get_geolocation(base_url:str, user:str, password:str):
    url = f"https://{base_url}/axis-cgi/geolocation/get.cgi"
    response = rest_request(method='GET', url=url, user=user, password=password)

    content = convert_xml(content=response.content.decode())
    if content:
        return {
            "lat": float(content['PositionResponse']['Success']['GetSuccess']['Location']['Lat']),
            "long": float(content['PositionResponse']['Success']['GetSuccess']['Location']['Lng'])
        }
    return {}