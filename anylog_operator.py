import argparse
import  anylog_support

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog REST connection')
    parse.add_argument('ledger_conn', type=str, default=None, help='TCP connection information for Ledger / Master node')
    parse.add_argument('--topic', type=str, default='axis', help='Message broker topic')
    args = parse.parse_args()

    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"id": args.topic})
    if not is_policy:
        policy = anylog_support.create_mapping_policy(policy_name=args.topic, dbms=args.dbms, table=args.table)
        anylog_support.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn, ledger_conn=args.ledger_conn)


    anylog_support.declare_mqtt_request(anylog_conn=args.anylog_conn, topic=args.topic)


if __name__ == '__main__':
    main()

