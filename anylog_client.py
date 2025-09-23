import argparse
import anylog_support
from __support__ import extract_credentials
from camera_functions import list_recordings, export_recording
import base64

def main():
    parse = argparse.ArgumentParser()
    parse.add_argument('video_conn',  type=str, default=None, help='connection information {USER}:{PASS}@{IP}:{PORT}')
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog credentials for sending data')
    parse.add_argument('--ledger-conn', type=str, required=False, default=None, help='master node / ledger IP:Port, if set declare policy')
    parse.add_argument('--camera-owner', type=str, required=False, default='Axis', help='Camera owner')
    parse.add_argument('--declare-policy', type=bool, nargs='?', const=True, default=False, help='Declare policy on blockchain')
    parse.add_argument('--dbms', type=str, default='axis', help='logical database to store data in')
    parse.add_argument('--table', type=str, default='camera1', help='table to store data')
    parse.add_argument('--topic', type=str, default='axis', help='sending data via POST topic')

    args = parse.parse_args()

    base_url, user, password = extract_credentials(conn_info=args.video_conn)
    # declare policy with info about camera
    if args.declare_policy:
        anylog_support.declare_policy(anylog_conn=args.anylog_conn, ledger_conn=args.ledger_conn, base_url=base_url, user=user, password=password)

    # list videos
    videos_list = []
    videos = list_recordings(base_url=base_url, user=user, password=password, record_id=None)
    if videos:
        for video in videos: # list of
            videos_list.append(video['@recordingid'])

        for recording_id in videos_list:
            recording_info = anylog_support.generate_data(base_url=base_url, user=user, password=password, record_id=recording_id)
            content, _, _ = export_recording(base_url=base_url, user=user, password=password, record_id=recording_id)
            recording_info['file_content'] = base64.b64encode(content).decode('utf-8')
            recording_info['file_type'] = 'video/mp4'

            anylog_support.publish_data(anylog_conn=args.anylog_conn, payload=recording_info, topic=args.topic, dbms=args.dbms, table=args.table)
            exit(1)

if __name__ == '__main__':
    main()
