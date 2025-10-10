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

    topic = "axis/B8A44FC5C075/event/tns:axis/CameraApplicationPlatform/ObjectAnalytics/Device1ScenarioANY"
    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": f"{args.topic}-insight"})
    if not is_policy:
        policy = anylog_support.create_data_mapping_policy(policy_name=f"{args.topic}-insight", dbms='axis', table="camera_insight",)
        anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=topic):
        anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='172.104.228.251', port=1883,
                                            user='anyloguser', password='mqtt4AnyLog!',
                                            topic=topic, policy_id=f"{args.topic}-insight")

    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": f"{args.topic}-new"})
    if not is_policy:
        policy = anylog_support.create_merged_policy(policy_name=f"{args.topic}-new", dbms='axis', table="camera_insight2",)
        anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    if not anylog_support.check_mqtt(anylog_conn=args.anylog_conn, topic=f"{args.topic}-new"):
        anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', port=32149,
                                            # user='anyloguser', password='mqtt4AnyLog!',
                                            topic=f"{args.topic}-new",
                                            policy_id=f"{args.topic}-new")

if __name__ == '__main__':
    main()

