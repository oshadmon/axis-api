import argparse

import camera_functions
import __support__
import __anylog_support__


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument('anylog_conn', type=str, default='127.0.0.1:32149', help='Operator REST IP:Port')
    parser.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parser.add_argument('--start-timestamp', type=str, default=None, help='newest')
    parser.add_argument('--topic', type=str, default='syslog', help='msg client topic for logs')
    parser.add_argument('--logical-database', type=str, default='axis', help='')
    args = parser.parse_args()

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)
    _, serial = __anylog_support__.create_camera_policy(camera_url, camera_user, camera_password)

    logs = camera_functions.get_syslogs(base_url=camera_url, user=camera_user, password=camera_password)
    for i in range(len(logs)):
        logs[i]['dbms'] = args.logical_database
        logs[i]['table'] = 'camera_syslog'
        logs[i]['serial'] = serial  # camera serial number

        logs[i]['timestamp'] = __support__.convert_to_utc(logs[i]['timestamp'])

        if not args.start_timestamp:
            logs[i]['timestamp'] = logs[i]['timestamp'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    if args.start_timestamp:
        publish_log = []
        for log in logs:
            if log['timestamp'] >= args.start_timestamp:
                log['timestamp'] = log['timestamp'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                publish_log.append(log)
    else:
        publish_log = logs
    data = {}
    for row in publish_log:
        for key in row:
            if key not in data:
                data[key] = {
                    'data_type': [],
                    'count': 0
                }

            if str(type(row[key])) not in data[key]['data_type']:
                data[key]['data_type'].append(str(type(row[key])))
            data[key]['count'] += 1
    import json
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()

