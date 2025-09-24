import argparse
import datetime

import anylog_support
from __support__ import extract_credentials
from camera_functions import list_recordings, export_recording
import base64
import json

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('video_conn',  type=str, default=None, help='connection information {USER}:{PASS}@{IP}:{PORT}')
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog credentials for sending data')
    parse.add_argument('--ledger-conn', type=str, required=False, default=None, help='master node / ledger IP:Port, if set declare policy')
    parse.add_argument('--camera-owner', type=str, required=False, default='Axis', help='Camera owner')
    parse.add_argument('--dbms', type=str, default='axis', help='logical database to store data in')
    parse.add_argument('--table', type=str, default=None, help='table to store data')
    parse.add_argument('--topic', type=str, default='axis', help='sending data via POST topic')

    args = parse.parse_args()

    base_url, user, password = extract_credentials(conn_info=args.video_conn)
    # declare policy with info about camera
    camera_policy, serial_num = anylog_support.create_camera_policy(base_url=base_url, user=user, password=password)
    if not args.table:
        args.table = f"camera_{str(serial_num).lower()}"
    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial_num})
    if not is_policy:
        anylog_support.declare_policy(raw_policy=camera_policy, anylog_conn=args.anylog_conn)

    payload = {
        "dbms": args.dbms, "table": args.table
    }
    # list videos
    videos_list = []
    videos = list_recordings(base_url=base_url, user=user, password=password, record_id=None)
    if videos:
        for video in videos: # list of
            videos_list.append(video['@recordingid'])

        for recording_id in videos_list:
            recording_info = anylog_support.generate_data(base_url=base_url, user=user, password=password, record_id=recording_id)
            recording_info["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            content, _, _ = export_recording(base_url=base_url, user=user, password=password, record_id=recording_id)
            recording_info['content'] = base64.b64encode(content).decode('utf-8')
            recording_info['file_type'] = 'mp4'
            payload.update(recording_info)

            anylog_support.publish_data(anylog_conn=args.anylog_conn, payload=payload, topic=args.topic)
            # exit(1)

if __name__ == '__main__':
    main()
