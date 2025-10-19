import argparse
import streaming_video

import __support__
import __anylog_support__
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera-conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    parser.add_argument('--logical-database', type=str, default='axis', help='logical database to store data in')
    args = parser.parse_args()

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)
    # create camera policy if DNE
    policy, serial = __anylog_support__.create_camera_policy(camera_url, camera_user, camera_password)
    # is_policy = __support__.check_policy(anylog_conn=args.anylog_conn, where_condition={"serial_number": serial})
    # if not is_policy: # declare camera policy
    #     __anylog_support__.declare_policy(raw_policy=policy, anylog_conn=args.anylog_conn)

    table_name=f"camera_{serial}"
    sv = streaming_video.StreamingVideo(base_url=camera_url, user=camera_user, password=camera_password,
                                        dbms=args.logical_database, table=table_name)
    sv.show_video()

        
if __name__ == '__main__':
    main()
