import json
import camera_functions


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


def declare_camera_policy(camera_url:str, camera_user:str, camera_password:str, anylog_conn:str, ledger_conn:str)
    camera_policy, serial_num = create_camera_policy(base_url=camera_url, user=camera_user, password=camera_password)
    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial_num})
    if not is_policy:
        anylog_support.declare_policy(raw_policy=camera_policy, anylog_conn=args.anylog_conn)


# def main():
#     """
#     Create mapping policy and `run msg client` against operator node to ingest data from videos
#     """
#     parse = argparse.ArgumentParser()
#     parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog REST connection')
#     parse.add_argument('ledger_conn', type=str, default=None, help='TCP connection information for Ledger / Master node')
#     parse.add_argument('--topic', type=str, default='axis', help='Message broker topic')
#     args = parse.parse_args()
#
#     is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.topic})
#     if not is_policy:
#         policy = anylog_support.create_camera_mapping_policy(policy_name=args.topic)
#         anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)
#         time.sleep(1)
#     if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=args.topic):
#         anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', topic=args.topic, policy_id=args.topic)
#
#     topic = "axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY"
#     is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": f"{args.topic}-insight"})
#     if not is_policy:
#         policy = anylog_support.create_data_mapping_policy(policy_name=f"{args.topic}-insight", dbms='axis', table="camera_insight", )
#         anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)
#
#     if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=topic):
#         anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='172.104.228.251', port=1883,
#                                             user='anyloguser', password='mqtt4AnyLog!',
#                                             topic=topic, policy_id=f"{args.topic}-insight")
#
#     is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": f"{args.topic}-new"})
#     if not is_policy:
#         policy = anylog_support.create_merged_policy(policy_name=f"{args.topic}-new", dbms='axis', table="camera_insight2", )
#         anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)
#
#     if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=f"{args.topic}-new"):
#         anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', port=32149,
#                                             # user='anyloguser', password='mqtt4AnyLog!',
#                                             topic=f"{args.topic}-new",
#                                             policy_id=f"{args.topic}-new")
#
# if __name__ == '__main__':
#     main()

