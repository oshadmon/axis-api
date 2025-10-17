import argparse
import __anylog_support__
import __support__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('anylog_conn', type=str, default=None, help='AnyLog / EdgeLake Operator IP and Port')
    parser.add_argument('--insight-topic', type=str, default=None, help='topic for insights (axis_demo.py)')
    parser.add_argument('--video-topic', type=str, default=None, help='topic for video storage (axis_demo_videos.py)')
    parser.add_argument('--logs-topic', type=str, default=None, help='topic for (sys) logs (axis_demo_logs.py)')
    args = parser.parse_args()

    topic = ""
    if args.insight_topic:
        is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.insight_topic})
        if not is_policy:
            policy = __anylog_support__.create_mapping_policy(policy_name=args.insight_topic, dbms="bring [dbms]",
                                                              table="bring [table]")
            __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

        if not __anylog_support__.check_mqtt(anylog_conn=args.anylog_conn, topic=args.insight_topic):
            topic += f"topic = (name={args.insight_topic} and policy={args.insight_topic}) and "

    if args.video_topic:
        is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.video_topic})
        if not is_policy:
            policy = __anylog_support__.create_video_mapping_policy(policy_name=args.video_topic, dbms="bring [dbms]",
                                                              table="bring [table]")
            __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

        if not __anylog_support__.check_mqtt(anylog_conn=args.anylog_conn, topic=args.video_topic):
            topic += f"topic = (name={args.video_topic} and policy={args.video_topic}) and "

    if args.logs_topic:
        is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.logs_topic})
        if not is_policy:
            policy = __anylog_support__.create_syslog_mapping_policy(policy_name=args.logs_topic, dbms="bring [dbms]",
                                                                    table="bring [table]")
            __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

        if not __anylog_support__.check_mqtt(anylog_conn=args.anylog_conn, topic=args.logs_topic):
            topic += f"topic = (name={args.logs_topic} and policy={args.logs_topic}) and "

    if topic:
        topic = topic.rsplit(" and ", 1)[0]
        __anylog_support__.declare_mqtt_request(broker='rest', anylog_conn=args.anylog_conn, topic=topic)


if __name__ == '__main__':
    main()
