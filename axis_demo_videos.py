import argparse
import base64
import datetime
import json
import __support__
import __anylog_support__
import camera_functions
import remote_mqtt_client


def create_payload(content:dict, dbms:str, table:str):
    payload = {
        "dbms": dbms, #
        "table": table, # string
        "recording": content.get('@recordingid'), #
        "start_time": content.get("@starttime"), # timestamp
        "end_time": content.get("@stoptime"), # timestamp
        "recording_type": content.get("@recordingtype"),   # string
        "event_id": content.get("@eventid"), # string
        "source": content.get("@source"), # int
        "mime_type": content['video'].get('@mimetype'), # string
        "resolution": content['video'].get('@resolution'), # string
        "frame_rate": content['video'].get('@framerate'), # string
        "width": content['video'].get('@width'), # int,
        "height": content['video'].get('@height')
    }

    payload['duration'] = __support__.validate_timestamp_format(payload['end_time']) - __support__.validate_timestamp_format(payload['start_time'])
    payload['duration'] = str(payload['duration'])

    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operator_conn', type=str, default='127.0.0.1:32149', help='Operator node IP:Port')
    parser.add_argument('query_conn', type=str, default='127.0.0.1:32049', help='Query node IP:Port')
    parser.add_argument('--operator-broker', type=str, default='127.0.0.1:32150', help='AnyLog broker IP:Port')
    parser.add_argument('camera_conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parser.add_argument('--logical-database', type=str, default='axis', help='logical database to store data in. same as snapshots')
    parser.add_argument('--topic', type=str, default='axis-videos', help='msg client policy topic + tag name')
    args = parser.parse_args()

    # create mapping policy
    is_policy = __support__.check_policy(anylog_conn=args.operator_conn, where_condition={"id": args.topic})
    if not is_policy:
        policy = __anylog_support__.create_mapping_policy(policy_name=args.topic, dbms="bring [dbms]",
                                                          table="bring [table]")
        __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.operator_conn)

    # msg client for AnyLog - using broker as it's a different policy
    if not __anylog_support__.check_mqtt(anylog_conn=args.operator_conn, topic=args.topic):
        __anylog_support__.declare_mqtt_request(anylog_conn=args.operator_conn, broker='local', port=32150,
                                                topic=args.topic, policy_id=args.topic)

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)
    _, serial = __anylog_support__.create_camera_policy(camera_url, camera_user, camera_password)
    snapshot_table = f"camera_{serial.lower()}" if serial else f"camera_unknown"
    video_table = f"videos_{snapshot_table.lower()}"

    output = __support__.rest_request(method='GET', url=f'http://{args.query_conn}',
                                      headers={
                                          'command': f"get tables where dbms={args.logical_database} and format=json",
                                          'User-Agent': 'AnyLog/1.23'
                                      })

    # check if tables exists
    existing_tables = list(output.json()[args.logical_database])
    new_recordings = []
    if snapshot_table in existing_tables:
        new_recordings = __anylog_support__.get_recordings(anylog_conn=args.query_conn, dbms=args.logical_database, table=snapshot_table)
        new_recordings = sorted(new_recordings)
    elif snapshot_table not in existing_tables:
        print(f'Camera insight table {snapshot_table} does not exist. cannot continue')
        exit(1)
    existing_records = []
    if video_table in existing_records:
        existing_records = __anylog_support__.get_recordings(anylog_conn=args.query_conn, dbms=args.logical_database, table=video_table)

    for recording in new_recordings:
        if recording not in existing_records:
            recording_info = camera_functions.list_recordings(base_url=camera_url, user=camera_user, password=camera_password, record_id=recording)
            duration = __support__.validate_timestamp_format(recording_info['@stoptime']) - __support__.validate_timestamp_format(recording_info['@starttime'])

            if duration <= datetime.timedelta(minutes=5) and recording_info.get('@recordingstatus') == 'completed':
                payload = create_payload(content=recording_info, dbms=args.logical_database, table=video_table)
                content, _, _ = camera_functions.export_recording(base_url=camera_url, user=camera_user,
                                                                  password=camera_password, record_id=recording)
                payload['file'] = base64.b64encode(content).decode('utf-8')
                remote_mqtt_client.mqtt_publish(conn=args.operator_broker, topic=args.topic, message=json.dumps(payload))
                existing_records.append(recording)





if __name__ == '__main__':
    main()
