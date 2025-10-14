import argparse
from mqtt_client import MqttClient

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
    # parse.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    # parse.add_argument('anylog_conn', type=str, default='127.0.0.1:32149', help='AnyLog Operator access')
    parse.add_argument('--mqtt-client', type=str, default='anyloguser:mqtt4AnyLog!@172.104.228.251:1883', help='MQTT connection information')
    parse.add_argument('--mqtt-topic', type=str, default="power-plant", help='MQTT topic')
    args = parse.parse_args() #"axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY"

    # connect to MQTT client
    mqttclient = MqttClient(conn=args.mqtt_client, topic=args.mqtt_topic)
    mqttclient.connect()

    # get data
    while True:
        msg = mqttclient.queue.get() # blocks until message arrives
        if msg:
            pass

    # content = {
    #     "topic":"axis:CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY",
    #     "timestamp":1759713693673,
    #     "serial":"B8A44FC5C075",
    #     "message":{
    #         "source":{},
    #         "key":{},
    #         "data":{
    #             "objectId":"370312",
    #             "active":"0",
    #             "classTypes":"human",
    #             "triggerTime": "2025-10-09T11:57:22.928315-04:00" # "2025-10-09T12:00:33.856-0400"
    #         }
    #     }
    # }
    #
    # # timestamp = content['message']['data']['triggerTime']
    # serial = content.get('serial')
    # payload = {
    #     "table": f"camera_{serial}" if serial else "camera_unknown",
    #     "recording_id": get_video(timestamp=content['message']['data'].get('triggerTime')),
    #     "timestamp": content.get('timestamp'),
    #     "object_id": content['message']['data'].get('objectId'),
    #     "object": content['message']['data'].get('classTypes'),
    #     "active": True if content['message']['data'].get('active') == 1 else False,
    #     "snapshot": snapshot(),  # jpg
    # }
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
