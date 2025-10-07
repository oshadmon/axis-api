import argparse
import datetime

import anylog_support
from __support__ import extract_credentials, validate_timestamp_format
from camera_functions import list_recordings, export_recording
import base64


def __publish_recording(anylog_conn:str, base_url:str, user:str, password:str, dbms:str, table:str, topic:str, start_timestamp:str=None):
    """
    "main" process for publishing recordings onto AnyLog via POST
    :args:
        anylog_conn:str - AnyLog credentials for sending data
        base_url:str - video IP:Port
        user:str | password:str - authentication credentials for video
        dbms:str - logical database
        table:str - logical table
        topic:str - POST topic
        start_timestamp:str - timestamp to start inserts from
    :params:
        video_timestamp_str - string format for current timestamp
        video_timestamp:datetime.datetime - video_timestamp_str in datetime format
        record_id:str - recording ID
        start_timestamp:datetime.datetime - start_timestamp in datetime format
        videos:list - list of videos
        payload:dict - insert payload
        recording_info:dict - recording information
        content:bytes - actual recording
    :return:
        last start_timestamp
    """
    video_timestamp_str = None
    start_timestamp = validate_timestamp_format(start_timestamp)
    videos = list_recordings(base_url=base_url, user=user, password=password, record_id=None)
    payload = {
        "dbms": dbms, "table": table
    }

    if videos:
        for video in videos:
            video_timestamp_str = video['@starttime']
            video_timestamp = validate_timestamp_format(video['@starttime'])
            recording_id = video['@recordingid']
            if not start_timestamp or video_timestamp >= start_timestamp:
                recording_info = anylog_support.generate_data(base_url=base_url, user=user, password=password, record_id=recording_id)
                recording_info["timestamp"] = datetime.datetime.now(tz=datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                content, _, _ = export_recording(base_url=base_url, user=user, password=password, record_id=recording_id)
                recording_info['content'] = base64.b64encode(content).decode('utf-8')
                recording_info['file_type'] = 'mp4'

                payload.update(recording_info)

                # publish payload
                anylog_support.publish_data(anylog_conn=anylog_conn, payload=payload, topic=topic)

    return video_timestamp_str # last video timestamp


def main():
    """
    Extract recordings from AXIS cameras and publish them onto AnyLog / EdgeLake via POST
    :steps:
        1. Start Operator node with NoSQL
        2. Enable msg client - anylog_operator.py
        3. Begin data transfer
    :positional arguments:
        video_conn            connection information {USER}:{PASS}@{IP}:{PORT}
        anylog_conn           AnyLog credentials for sending data
    :options:
        -h, --help                          show this help message and exit
        --camera-owner      CAMERA_OWNER        camera owner
        --dbms              DBMS                logical database to store data in
        --table             TABLE               table to store data
        --topic             TOPIC               sending data via POST topic
        --start-timestamp   START_TIMESTAMP     Start timestamp (format: Y-m-d H:M:S)
        --continuous        [CONTINUOUS]        repeat video pull each time process finishes and start
    :params:
        base_url:str - video IP:Port
        user:str | password:str - authentication credentials for video
        camera_policy:str - generated AnyLog policy for camera
        is_policy:bool - whether camera policy exists
    :print:
        if not continuous, prints the last recording timestamp
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('video_conn',  type=str, default=None, help='connection information {USER}:{PASS}@{IP}:{PORT}')
    parse.add_argument('anylog_conn', type=str, default=None, help='AnyLog credentials for sending data')
    parse.add_argument('--camera-owner', type=str, required=False, default='Axis', help='Camera owner')
    parse.add_argument('--dbms', type=str, default='axis', help='logical database to store data in')
    parse.add_argument('--table', type=str, default=None, help='table to store data')
    parse.add_argument('--topic', type=str, default='axis', help='sending data via POST topic')
    parse.add_argument('--start-timestamp', type=str, default=None, help='Start timestamp (format: Y-m-d H:M:S')
    parse.add_argument('--continuous', type=bool, nargs='?', const=True, default=False, help='repeat video pull each time process finishes')
    args = parse.parse_args()

    base_url, user, password = extract_credentials(conn_info=args.video_conn)

    # declare policy with info about camera
    camera_policy, serial_num = anylog_support.create_camera_policy(base_url=base_url, user=user, password=password)
    if not args.table:
        args.table = f"camera_{str(serial_num).lower()}"
    is_policy = anylog_support.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial_num})
    if not is_policy:
        anylog_support.declare_policy(raw_policy=camera_policy, anylog_conn=args.anylog_conn)

    # publish videos
    if args.continuous:
        while True:
            args.start_timestamp = __publish_recording(anylog_conn=args.anylog_conn, base_url=base_url, user=user,
                                                       password=password, dbms=args.dbms, table=args.table,
                                                       topic=args.topic, start_timestamp=args.start_timestamp)
    else:
        args.start_timestamp = __publish_recording(anylog_conn=args.anylog_conn, base_url=base_url, user=user,
                                                   password=password, dbms=args.dbms, table=args.table,
                                                   topic=args.topic, start_timestamp=args.start_timestamp)
    print(f"Last Timestamp: {args.start_timestamp}")


if __name__ == '__main__':
    main()
