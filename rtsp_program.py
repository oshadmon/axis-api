import argparse
import streaming_video

import __support__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera-conn', type=str, default='AnyLog:OriIsTheBest#1!@166.143.227.89', help='access information for Axis camera')
    args = parser.parse_args()

    camera_url, camera_user, camera_password = __support__.extract_credentials(conn_info=args.camera_conn)

    rtsp_url = f"rtsp://{camera_user}:{camera_password}@{camera_url}:554/axis-media/media.amp?videocodec=h264"

    sv = streaming_video.StreamingVideo(base_url=camera_url, user=camera_user, password=camera_password)
    sv.show_video()

        
if __name__ == '__main__':
    main()
