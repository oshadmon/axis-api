import av
import cv2
from urllib.parse import quote
import threading

class RTSPServer:
    def __init__(self, base_url: str, user: str, password: str, port: int = 554):
        self.base_url = base_url
        self.camera_user = user
        self.camera_password = password

        self.rtsp_url = (
            f"rtsp://{self.camera_user}:{quote(password)}@"
            f"{self.base_url}:{port}/axis-media/media.amp?videocodec=h264"
        )
        self.options = {
            "rtsp_transport": "tcp",
            "stimeout": "5000000",
            "fflags": "nobuffer",
            "max_delay": "0",
        }

        self.container = self.open_connection()
        self.hide_video = False
        self.user_input = ""
        self.running = True

        # start background thread for keyboard input
        threading.Thread(target=self._read_input, daemon=True).start()

    def _read_input(self):
        """Read user input from console to control window."""
        while self.running:
            key = input().strip().lower()
            if key in ("h", "s", "q"):
                self.user_input = key

    def __imshow(self, img):
        """Show or hide OpenCV window based on toggle."""
        if self.hide_video:
            cv2.destroyAllWindows()
            return
        try:
            cv2.imshow("Axis Stream", img)
        except cv2.error as e:
            print(f"[OpenCV] Warning: {e}")

    def open_connection(self):
        """Open RTSP stream."""
        try:
            return av.open(self.rtsp_url, options=self.options, timeout=30)
        except Exception as error:
            raise Exception(f"Failed to open RTSP: {error}")

    def close_connection(self):
        """Close RTSP stream."""
        try:
            if self.container:
                self.container.close()
        except Exception as error:
            print(f"Warning: failed to close RTSP ({error})")

    def stream_video(self):
        """Decode and display video stream."""
        try:
            stream = self.container.streams.video[0]
            print("Commands: [h]=hide, [s]=show, [q]=quit")

            for packet in self.container.demux(stream):
                if packet.stream.type != "video":
                    continue

                for frame in packet.decode():
                    img = frame.to_ndarray(format="bgr24")

                    # handle user input
                    if self.user_input == "h":
                        self.hide_video = True
                        self.user_input = ""
                        print("🔕 Video hidden")
                    elif self.user_input == "s":
                        self.hide_video = False
                        self.user_input = ""
                        print("👁️ Video shown")
                    elif self.user_input == "q":
                        print("🛑 Quitting...")
                        return

                    self.__imshow(img)
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                        return

        except Exception as error:
            print(f"[Error] Failed to stream video: {error}")
        finally:
            self.running = False
            self.close_connection()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    rtsp_server = RTSPServer( base_url="166.143.227.89", user="AnyLog", password="OriIsTheBest#1!@")
    rtsp_server.stream_video()
