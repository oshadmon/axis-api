import argparse
import anylog_support
from __support__ import extract_credentials

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('video_conn',  type=str, default=None, help='connection information {USER}:{PASS}@{IP}:{PORT}')
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog credentials for sending data')
    parse.add_argument('--ledger-conn', type=str, required=False, default=None, help='master node / ledger IP:Port, if set declare policy')
    parse.add_argument('--camera-owner', type=str, required=False, default='Axis', help='Camera owner')
    parse.add_argument('--declare-policy', type=bool, nargs='?', const=True, default=False, help='Declare policy on blockchain')
    args = parse.parse_args()

    base_url, user, password = extract_credentials(conn_info=args.video_conn)
    if args.declare_policy:
        anylog_support.declare_policy(anylog_conn=args.anylog_conn, ledger_conn=args.ledger_conn, base_url=base_url, user=user, password=password)



if __name__ == '__main__':
    main()
