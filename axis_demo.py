import argparse
import base64
import datetime
# import json

import __anylog_support__
import __support__
import remote_mqtt_client
import camera_functions

def __tmp_create_msg()->dict:
    """
    tmp function to create an mqtt output message until we have a "prod" env
    :return:
    """
    import random
    objects = {
        "human": "370312",
        "truck": "380491",
        "car"  : "480298",
    }

    object = random.choice(list(objects))
    timestamp = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=random.choice(list(range(-2, 0))), hours=random.choice(list(range(-23, 23))), minutes=random.choice(list(range(-59, 59))), seconds=random.choice(list(range(-59, 59))))

    payload = {  # this will disappear once we have it working properly
        "topic": "axis:CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY",
        "timestamp": int(timestamp.timestamp()),
        "serial": "B8A44FC5C075",
        "message": {
            "source": {},
            "key": {},
            "data": {
                "objectId": objects[object],
                "active": random.choice([0, 1]) ,
                "classTypes": object,
                "triggerTime": timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        }
    }

    return payload


def build_payload(msg:dict, serial_id:str, logical_database:str, camera_url, camera_user, camera_password):

    snapshot = camera_functions.take_snapshot(base_url=camera_url, user=camera_user, password=camera_password)
    recording_id = camera_functions.id_by_timestamp(base_url=camera_url, user=camera_user, password=camera_password,
                                                    timestamp=msg['message']['data'].get('triggerTime'))
    recording_info = camera_functions.list_recordings(base_url=camera_url, user=camera_user, password=camera_password,
                                                      record_id=recording_id)
    payload = {
        "dbms": logical_database,
        "table": f"camera_{serial_id}" if serial_id else "camera_unknown",
        "timestamp": msg.get('timestamp'),
        "start_time": recording_info.get('@starttime'),
        "end_time": recording_info.get('@stoptime'),
        "recording": recording_id,
        'recording_status': recording_info.get('@recordingstatus'),
        'object_id': msg['message']['data'].get('objectId'),
        'object': msg['message']['data'].get('classTypes'),
        "snapshot": base64.b64encode(snapshot).decode("utf-8")
    }

    # extract information from message to payload
    try:
        payload['active'] = True if int(msg['message']['data'].get('active')) == 1 else False
    except:
        payload['active'] = False


    return payload



def main():
    print(f"Start Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    parser = argparse.ArgumentParser()
    parser.add_argument('anylog_conn', type=str, default='127.0.0.1:32149', help='Operator REST IP:Port')
    parser.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parser.add_argument('--topic', type=str, default='axis-data', help='Topic to use against AnyLog REST message client')
    parser.add_argument('--logical-database', type=str, default='axis', help='logical database to store data in')
    args = parser.parse_args()


    if not args.topic:
        raise ValueError(f"Missing Topic value - topic required")

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)

    # create camera policy if DNE
    policy, serial = __anylog_support__.create_camera_policy(camera_url, camera_user, camera_password)
    is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial})
    if not is_policy: # create policy
        __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    # create mapping policy
    is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.topic})
    if not is_policy:
        policy = __anylog_support__.create_mapping_policy(policy_name=args.topic, dbms="bring [dbms]", table="bring [table]")
        __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    # msg client for AnyLog
    if not __anylog_support__.check_mqtt(anylog_conn=args.anylog_conn, topic=args.topic):
        __anylog_support__.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', port=32149,
                                            topic=f"topic=(name{args.topic} and policy={args.topic})")


    msg_client = remote_mqtt_client.MqttClient(conn='anyloguser:mqtt4AnyLog!@172.104.228.251:1883',
                                               topic='axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY')

    # msg_client = remote_mqtt_client.MqttClient(conn='anyloguser:mqtt4AnyLog!@172.104.228.251:1883', topic="power-plant")
    msg_client.connect()
    while True:
        msg = msg_client.queue.get()
        # msg = __tmp_create_msg() # dummy message client payload

        payload = build_payload(msg=msg, logical_database=args.logical_database, serial_id=serial, camera_url=camera_url,
                                camera_user=camera_user, camera_password=camera_password)

        __anylog_support__.publish_data(anylog_conn=args.anylog_conn, topic=args.local_camera_topic, payload=payload)










if __name__ == '__main__':
    main()