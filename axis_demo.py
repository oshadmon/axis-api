import argparse
import base64
import os

import anylog_policies
from camera_functions import id_by_timestamp, take_snapshot
from mqtt_client import MqttClient
from __support__ import extract_credentials, create_merged_policy


def snapshot(base_url:str, user:str, password:str):
    """
    take a snapshot + read its content to be stored
    """
    take_snapshot(base_url=base_url, user=user, password=password)
    filepath = os.path.join('../data', 'snapshot.jpg')

    with open(filepath, 'rb') as fwrite:
        encoded_string = base64.b64encode(fwrite.read()).decode("utf-8")

    return encoded_string


def main():
    """
    :Logic:
        1. connect to camera
        2. connect to mqtt client
        3. when content comes from MQTT client take snapshot
        4. store content from MQTT client + snapshot + recording ID in AnyLog / EdgeLake
    :return:
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parse.add_argument('anylog_conn', type=str, default='127.0.0.1:32149', help='AnyLog Operator access')
    parse.add_argument('--mqtt-client', type=str, default='anyloguser:mqtt4AnyLog!@172.104.228.251:1883', help='MQTT connection information')
    parse.add_argument('--ledger-conn', type=str, default=None, help='if provided ( [IP]:[PORT] ) declare policy on blockchain')
    parse.add_argument('--policy-name', type=str, default='camera-mapping-policy', help='mapping policy name')
    parse.add_argument('--axis-topic', type=str, default='power-plant', help='Axis logical topic') #"axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY"
    parse.add_argument('--mqtt-topic', type=str, default="axis-demo", help='REST (local) topic')
    args = parse.parse_args()

    camera_url, camera_user, camera_password = extract_credentials(conn_info=args.camera_conn)

    anylog_policies.declare_camera_policy(camera_url=camera_password, camera_user=camera_password,
                                          camera_password=camera_password, anylog_conn=args.anylog_conn,
                                          ledger_conn=args.ledger_conn) # camera policy

    anylog_policies.declare_mapping_policy(anylog_conn=args.anylog_conn,
                                           policy_id=f"{args.mqtt-topic.relace(' ', '-')}-mapping",
                                           dbms="bring [dbms]", table="bring [table]") # mapping policy

    # run msg client (REST)
    anylog_policies.declare_msg_client(anylog_conn=args.anylog_conn,
                                       policy_id=f"{args.mqtt-topic.relace(' ', '-')}-mapping")

    # connect to MQTT client
    mqttclient = MqttClient(conn=args.mqtt_client, topic=args.mqtt_topic)
    mqttclient.connect()

    # get data
    payload = {}
    while True:
        content = mqttclient.queue.get() # blocks until message arrives
        if content:
            content = {
                "topic":"axis:CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY",
                "timestamp":1759713693673,
                "serial":"B8A44FC5C075",
                "message":{
                    "source":{},
                    "key":{},
                    "data":{
                        "objectId":"370312",
                        "active":"0",
                        "classTypes":"human",
                        "triggerTime": "2025-10-09T11:57:22.928315-04:00" # "2025-10-09T12:00:33.856-0400"
                    }
                }
            }

            serial = content.get('serial')
            payload.update({
                "table": f"camera_{serial}" if serial else "camera_unknown",
                "recording_id": id_by_timestamp(base_url=camera_url, user=camera_user, password=camera_password, timestamp=content['message']['data'].get('triggerTime')),
                "timestamp": content.get('timestamp'),
                "object_id": content['message']['data'].get('objectId'),
                "object": content['message']['data'].get('classTypes'),
                "active": True if content['message']['data'].get('active') == 1 else False,
                "snapshot": snapshot(base_url=camera_url, user=camera_user, password=camera_password),  # jpg
            })



    # # timestamp = content['message']['data']['triggerTime']
    # serial = content.get('serial')

    # # video_payload = get_video(timestamp=content['message']['data']['triggerTime'])
    # # if video_payload:
    # #     payload.update(video_payload)
    #
    # rest_request(method='POST', url='http://173.255.230.238:32149',
    #              headers={
    #                  'command': 'data',
    #                  'topic': 'axis-new',
    #                  'User-Agent': 'AnyLog/1.23',
    #                  'Content-Type': 'text/plain'
    #              }, data_payload=json.dumps(payload))
    #



if __name__ == '__main__':
    main()
