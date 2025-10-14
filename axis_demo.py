import argparse
import __anylog_support__
import __support__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('anylog_conn', type=str, default='127.0.0.1:32149', help='Operator REST IP:Port')
    parser.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parser.add_argument('--policy-id', type=str, default=None, help='Mapping policy ID')
    parser.add_argument('--local-camera-topic', type=str, default='axis-cameras', help='Topic to use against AnyLog REST message client')
    args = parser.parse_args()

    if not args.policy_id:
        args.policy_id = args.local_camera_topic

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)
    # create camera policy if DNE
    policy, serial = __anylog_support__.create_camera_policy(camera_url, camera_user, camera_password)
    is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial})
    if not is_policy: # create policy
        __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    # create mapping policy
    is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.policy_id})
    if not is_policy:
        policy = __anylog_support__.create_mapping_policy(policy_name=args.policy_id, dbms="bring [dbms]", table="bring [table]")
        __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    # msg client for AnyLog
    if not __anylog_support__.check_mqtt(anylog_conn=args.anylog_conn, topic=args.local_camera_topic):
        __anylog_support__.declare_mqtt_request(anylog_conn=args.anylog_conn, broker='rest', port=32149,
                                            topic=args.local_camera_topic,
                                            policy_id=args.policy_id)

    # declare msg client

if __name__ == '__main__':
    main()