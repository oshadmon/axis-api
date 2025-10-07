import argparse
import time

import  anylog_support

def main():
    """
    Create mapping policy and `run msg client` against operator node to ingest data from videos
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog REST connection')
    parse.add_argument('ledger_conn', type=str, default=None, help='TCP connection information for Ledger / Master node')
    parse.add_argument('--topic', type=str, default='axis', help='Message broker topic')
    args = parse.parse_args()

    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.topic})
    if not is_policy:
        policy = anylog_support.create_camera_mapping_policy(policy_name=args.topic)
        anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)
        time.sleep(1)
    if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=args.topic):
        anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', topic=args.topic, policy_id=args.topic)

    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": f"{args.topic}-insight"})
    if not is_policy:
        policy = anylog_support.create_data_mapping_policy(policy_name=f"{args.topic}-insight", dbms='axis', table="camera_insight",)
        anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)
        time.sleep(1)
    if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=f"{args.topic}-insight"):
        anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='172.104.228.251', port=1883,
                                            user='anyloguser', password='mqtt4AnyLog!',
                                            topic="axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/#",
                                            policy_id=f"{args.topic}-insight")



if __name__ == '__main__':
    main()

